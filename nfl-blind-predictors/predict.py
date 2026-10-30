"""Ask all 100 predictors about one upcoming NFL game.

Each predictor learns from the N most recent finished games (the same
amounts as in experiment.py), then picks a winner.

Usage:
    python predict.py HOME_TEAM AWAY_TEAM
    python predict.py KC BUF
"""

import sys
from collections import Counter

from experiment import load_games
from predictors import build_predictors, game_counts, team_name


def main(argv):
    if len(argv) != 3:
        print(__doc__.strip())
        return 1

    home, away = team_name(argv[1].upper()), team_name(argv[2].upper())
    games = load_games()
    if home not in {g["home"] for g in games} or away not in {g["home"] for g in games}:
        print("Use team abbreviations like KC, BUF, PHI, SF, NYG.")
        return 1

    counts = game_counts(len(games))
    votes = Counter()
    print(f"{away} at {home}\n")
    for predictor, n in zip(build_predictors(len(counts)), counts):
        predictor.train(games[len(games) - n:] if n else [])
        pick = predictor.predict(home, away)
        votes[pick] += 1
        margin = abs(predictor.predicted_margin(home, away))
        print(f"  #{predictor.predictor_id:>3}  {n:>5} games  ->  {pick} by {margin:.1f}")

    print(f"\nVotes: {home} {votes[home]}, {away} {votes[away]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

"""Ask all 100 predictors about one upcoming NFL game.

Each predictor learns from the N most recent finished games (the same
amounts as in experiment.py), then picks a winner.

Usage:
    python predict.py HOME_TEAM AWAY_TEAM
    python predict.py KC BUF
"""

import sys
from collections import Counter

from data import FEATURES, load_games, team_name
from predictors import build_predictors, game_counts


def main(argv):
    if len(argv) != 3:
        print(__doc__.strip())
        return 1

    home, away = team_name(argv[1].upper()), team_name(argv[2].upper())
    games, _, tracker = load_games()
    if home not in tracker.results or away not in tracker.results:
        print("Use team abbreviations like KC, BUF, PHI, SF, NYG.")
        return 1

    home_f, away_f = tracker.features(home), tracker.features(away)
    features = [home_f[k] - away_f[k] for k in FEATURES]
    counts = game_counts(len(games))
    votes = Counter()
    print(f"{away} ({tracker.record_text(away)}) at {home} ({tracker.record_text(home)})\n")
    for predictor, n in zip(build_predictors(len(counts)), counts):
        predictor.train(games[len(games) - n:] if n else [])
        pick = predictor.predict(home, away, features)
        votes[pick] += 1
        margin = abs(predictor.predicted_margin(home, away, features))
        print(f"  #{predictor.predictor_id:>3}  {n:>5} games  ->  {pick} by {margin:.1f}")

    print(f"\nVotes: {home} {votes[home]}, {away} {votes[away]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

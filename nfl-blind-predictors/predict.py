"""Run all 100 blind predictors on one NFL game.

Usage:
    python predict.py HOME_TEAM AWAY_TEAM
    python predict.py Chiefs Bills
"""

import sys
from collections import Counter

from predictors import build_predictors


def main(argv):
    if len(argv) != 3:
        print(__doc__.strip())
        return 1

    home_team, away_team = argv[1], argv[2]
    predictors = build_predictors()
    picks = [p.predict(home_team, away_team) for p in predictors]

    print(f"{away_team} at {home_team}: {len(picks)} predictors, no data\n")
    for pick in picks:
        print(
            f"  #{pick['predictor']:>3}  {pick['winner']} {pick['score']}"
            f"  ({pick['confidence']:.0%} sure)"
        )

    votes = Counter(pick["winner"] for pick in picks)
    print("\nVotes:")
    for team in (home_team, away_team):
        print(f"  {team}: {votes[team]}")

    leader, leader_votes = votes.most_common(1)[0]
    if leader_votes * 2 == len(picks):
        print("\nConsensus: dead even tie")
    else:
        print(f"\nConsensus: {leader} ({leader_votes}/{len(picks)})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

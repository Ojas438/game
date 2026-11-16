"""Redo the weeks 8-10 picks with version 2 of the predictors.

The first three sets of picks (Nov 1, 3 and 11, 2026) were made with
version 1. This makes each set again with version 2, as if it had been made
on its original date: games on or after that date count as not played, so
the predictors only see what was known then. The version 1 picks are kept
in picks/version1/.

These picks were made after the games were played, so they are a re-test,
not live predictions. Live version 2 picks start with week 11.

Usage:
    python redo_version2.py
"""

import csv
import os

from data import FEATURES, load_games, recent
from predictors import build_predictors, game_counts

HERE = os.path.dirname(os.path.abspath(__file__))
OLD_DIR = os.path.join(HERE, "picks", "version1")
NEW_DIR = os.path.join(HERE, "picks")
DATES = ["2026-11-01", "2026-11-03", "2026-11-11"]


def main():
    for date in DATES:
        with open(os.path.join(OLD_DIR, f"{date}.csv"), newline="") as f:
            matchups = next(csv.reader(f))[2:]
        games, upcoming, tracker = load_games(as_of=date)
        by_matchup = {f"{g['away']} at {g['home']}": g for g in upcoming}
        to_pick = [by_matchup[m] for m in matchups]
        pool = recent(games, to_pick[0]["season"])
        counts = game_counts(len(pool))
        predictors = build_predictors(len(counts))
        for predictor, n in zip(predictors, counts):
            predictor.train(pool[len(pool) - n:] if n else [])

        with open(os.path.join(NEW_DIR, f"{date}.csv"), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["predictor", "games_learned_from"] + matchups)
            for predictor, n in zip(predictors, counts):
                row = [predictor.predictor_id, n]
                for g in to_pick:
                    home_f, away_f = tracker.features(g["home"]), tracker.features(g["away"])
                    features = [home_f[k] - away_f[k] for k in FEATURES]
                    row.append(predictor.predict(g["home"], g["away"], features, g["neutral"]))
                writer.writerow(row)
        print(f"{date}: redid {len(matchups)} games, predictors learned from 0 to {len(pool)} games")


if __name__ == "__main__":
    main()

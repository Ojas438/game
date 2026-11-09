"""Which kind of data matters most? Leave each one out and see.

Runs the same test as experiment.py (100 predictors, 2021-2025 seasons) six
times: with all four stats, with none (scores only), and with each stat left
out in turn. A left-out stat is set to 0 for every game, so the predictor
can't use it.

Usage:
    python ablation.py

Writes results/ablation.csv.
"""

import csv
import os

from data import FEATURES, load_games
from experiment import TEST_SEASONS
from predictors import build_predictors, game_counts

RESULTS_FILE = os.path.join(os.path.dirname(__file__), "results", "ablation.csv")

VERSIONS = {"All four stats": FEATURES, "Scores only": []}
VERSIONS.update({f"No {name}": [f for f in FEATURES if f != name] for name in FEATURES})


def keep_only(games, kept):
    """Copies of the games with every stat not in `kept` set to 0."""
    mask = [1.0 if f in kept else 0.0 for f in FEATURES]
    return [{**g, "features": [x * m for x, m in zip(g["features"], mask)]} for g in games]


def run(games, kept):
    seasons = [
        ([g for g in games if g["season"] < s],
         [g for g in games if g["season"] == s and g["margin"] != 0])
        for s in TEST_SEASONS
    ]
    max_games = min(len(history) for history, _ in seasons)
    counts = game_counts(max_games)
    correct = [0] * len(counts)
    total = 0
    for season, (history, tests) in zip(TEST_SEASONS, seasons):
        history, tests = keep_only(history, kept), keep_only(tests, kept)
        total += len(tests)
        for i, (predictor, n) in enumerate(zip(build_predictors(len(counts), seed=season), counts)):
            predictor.train(history[len(history) - n:] if n else [])
            for g in tests:
                winner = g["home"] if g["margin"] > 0 else g["away"]
                if predictor.predict(g["home"], g["away"], g["features"], g["neutral"]) == winner:
                    correct[i] += 1
    return counts, [100.0 * c / total for c in correct]


def main():
    games, _, _ = load_games()
    results = {}
    for name, kept in VERSIONS.items():
        counts, accuracy = run(games, kept)
        results[name] = accuracy
        best = max(accuracy)
        print(f"{name:15} best {best:.1f}% at {counts[accuracy.index(best)]:>5} games, "
              f"all data {accuracy[-1]:.1f}%")

    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
    with open(RESULTS_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["predictor", "training_games"] + list(results))
        for i, n in enumerate(counts):
            writer.writerow([i + 1, n] + [f"{results[name][i]:.2f}" for name in results])
    print(f"\nFull results: {os.path.relpath(RESULTS_FILE)}")


if __name__ == "__main__":
    main()

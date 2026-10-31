"""Does giving a predictor more games make it better, and when does it stop helping?

All 100 predictors run identical code. Predictor 1 gets 0 games to learn
from, predictor 100 gets every game available, and the rest get amounts in
between. Each one is then tested on seasons it never saw.

To get enough test games for the differences to mean something, this runs
once per test season (2021 to 2025). For each test season a predictor gets
the N most recent games played *before* that season, then predicts every
game of that season. Accuracy is averaged over all test games.

Usage:
    python experiment.py

Writes results/results.csv.
"""

import csv
import math
import os
import time

from data import load_games
from predictors import build_predictors, game_counts

RESULTS_FILE = os.path.join(os.path.dirname(__file__), "results", "results.csv")
TEST_SEASONS = [2021, 2022, 2023, 2024, 2025]

# "Close enough to the best" for deciding where extra data stops paying off.
GOOD_ENOUGH_POINTS = 1.0


def main():
    games, _, _ = load_games()
    seasons = {
        season: (
            [g for g in games if g["season"] < season],
            [g for g in games if g["season"] == season and g["margin"] != 0],
        )
        for season in TEST_SEASONS
    }
    # Every test season must be able to supply the largest amount of history.
    max_games = min(len(history) for history, _ in seasons.values())
    counts = game_counts(max_games)
    total_tests = sum(len(tests) for _, tests in seasons.values())

    print(f"Test games: {total_tests} (seasons {TEST_SEASONS[0]}-{TEST_SEASONS[-1]})")
    print(f"Training games given out: 0 up to {max_games}\n")

    correct = [0] * len(counts)
    seconds = [0.0] * len(counts)
    for season, (history, tests) in seasons.items():
        predictors = build_predictors(len(counts), seed=season)
        for i, (predictor, n) in enumerate(zip(predictors, counts)):
            start = time.perf_counter()
            predictor.train(history[len(history) - n:] if n else [])
            seconds[i] += time.perf_counter() - start
            for g in tests:
                winner = g["home"] if g["margin"] > 0 else g["away"]
                if predictor.predict(g["home"], g["away"], g["features"], g["neutral"]) == winner:
                    correct[i] += 1

    accuracies = [100.0 * c / total_tests for c in correct]
    best = max(accuracies)
    good_enough = next(
        i for i, a in enumerate(accuracies) if a >= best - GOOD_ENOUGH_POINTS
    )
    # About 95% of the time, the true accuracy is within this many points.
    margin_of_error = 100 * 1.96 * math.sqrt(0.25 / total_tests)

    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
    with open(RESULTS_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "predictor", "training_games", "accuracy_percent",
            "change_from_previous", "change_per_100_extra_games",
            "training_seconds",
        ])
        print(f"{'pred':>4} {'games':>6} {'accuracy':>9} {'change':>7}")
        for i, (n, acc) in enumerate(zip(counts, accuracies)):
            change = acc - accuracies[i - 1] if i else 0.0
            per_100 = 100 * change / (n - counts[i - 1]) if i else 0.0
            writer.writerow([
                i + 1, n, f"{acc:.2f}", f"{change:+.2f}", f"{per_100:+.3f}",
                f"{seconds[i]:.4f}",
            ])
            print(f"{i + 1:>4} {n:>6} {acc:>8.1f}% {change:>+6.1f}")

    spread_tests = [
        g for _, tests in seasons.values() for g in tests if g["spread"]
    ]
    vegas = 100.0 * sum(
        (g["spread"] > 0) == (g["margin"] > 0) for g in spread_tests
    ) / len(spread_tests)

    print(f"\nMargin of error on each accuracy: about +/-{margin_of_error:.1f} points")
    print(f"No data (predictor 1):     {accuracies[0]:.1f}%")
    print(f"Best predictor:            {best:.1f}% "
          f"(predictor {accuracies.index(best) + 1}, "
          f"{counts[accuracies.index(best)]} games)")
    print(f"Within {GOOD_ENOUGH_POINTS:g} point of best at:  "
          f"{counts[good_enough]} games (predictor {good_enough + 1})")
    print(f"Betting favorites (for comparison): {vegas:.1f}%")
    print(f"Training time, {counts[good_enough]} games vs {max_games}: "
          f"{seconds[good_enough]:.2f}s vs {seconds[-1]:.2f}s")
    print(f"\nFull results: {os.path.relpath(RESULTS_FILE)}")


if __name__ == "__main__":
    main()

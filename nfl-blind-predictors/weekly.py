"""The weekly routine: update the data, lock in picks, and score them.

Usage:
    python weekly.py update   # download the latest scores and trades
    python weekly.py pick     # save all 100 predictors' picks for the next week
    python weekly.py score    # score every saved pick against the real results

Each week, run "update" and then "pick" before the first game of the week
(usually Thursday). After the games, run "update" and then "score".

Picks are saved in picks/<date>.csv and are never changed after that.
"pick" and "score" also rebuild the website with the latest picks and results.
A game that was already picked in an earlier file is not picked again.
"""

import csv
import datetime
import glob
import io
import os
import sys
import urllib.request

from data import FEATURES, GAMES_FILE, TRADES_FILE, load_games
from predictors import build_predictors, game_counts

HERE = os.path.dirname(os.path.abspath(__file__))
PICKS_DIR = os.path.join(HERE, "picks")
SCOREBOARD_FILE = os.path.join(HERE, "results", "season_scoreboard.csv")
SOURCE = "https://raw.githubusercontent.com/nflverse/nfldata/master/data/"

GAME_COLUMNS = ["season", "game_type", "week", "gameday", "home_team", "away_team",
                "home_score", "away_score", "location", "spread_line"]


def download(name, columns, rename=None, out_file=None):
    with urllib.request.urlopen(SOURCE + name) as response:
        rows = list(csv.DictReader(io.StringIO(response.read().decode("utf-8"))))
    rename = rename or {}
    with open(out_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        for row in rows:
            writer.writerow([row[rename.get(c, c)] for c in columns])
    return len(rows)


def update():
    games = download("games.csv", GAME_COLUMNS, out_file=GAMES_FILE)
    trades = download(
        "trades.csv",
        ["trade_id", "season", "trade_date", "gave", "received", "player",
         "pick_season", "pick_round"],
        rename={"player": "pfr_name"},
        out_file=TRADES_FILE,
    )
    print(f"Updated: {games} games, {trades} trade records.")


def matchup(game):
    return f"{game['away']} at {game['home']}"


def saved_picks():
    """Every saved picks file, as (date, header, rows), oldest first."""
    files = []
    for path in sorted(glob.glob(os.path.join(PICKS_DIR, "????-??-??.csv"))):
        with open(path, newline="") as f:
            rows = list(csv.reader(f))
        files.append((os.path.basename(path)[:10], rows[0], rows[1:]))
    return files


def pick():
    games, upcoming, tracker = load_games()
    today = datetime.date.today().isoformat()
    already = {(date, m) for date, header, _ in saved_picks() for m in header[2:]}
    already_matchups = {m for _, m in already}
    upcoming = [g for g in upcoming if g["date"] >= today]
    if not upcoming:
        print("No upcoming games on the schedule.")
        return
    week = (upcoming[0]["season"], upcoming[0]["week"])
    to_pick = [g for g in upcoming
               if (g["season"], g["week"]) == week and matchup(g) not in already_matchups]
    if not to_pick:
        print("Every game this week has already been picked.")
        return

    counts = game_counts(len(games))
    predictors = build_predictors(len(counts))
    for predictor, n in zip(predictors, counts):
        predictor.train(games[len(games) - n:] if n else [])

    path = os.path.join(PICKS_DIR, f"{today}.csv")
    if os.path.exists(path):
        print(f"{os.path.relpath(path)} already exists. Picks are never overwritten.")
        return
    os.makedirs(PICKS_DIR, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["predictor", "games_learned_from"] + [matchup(g) for g in to_pick])
        for predictor, n in zip(predictors, counts):
            row = [predictor.predictor_id, n]
            for g in to_pick:
                home_f, away_f = tracker.features(g["home"]), tracker.features(g["away"])
                features = [home_f[k] - away_f[k] for k in FEATURES]
                row.append(predictor.predict(g["home"], g["away"], features, g["neutral"]))
            writer.writerow(row)

    print(f"Saved picks for {len(to_pick)} games to {os.path.relpath(path)}\n")
    with open(path, newline="") as f:
        rows = list(csv.reader(f))
    for i, g in enumerate(to_pick, start=2):
        home_votes = sum(r[i] == g["home"] for r in rows[1:])
        print(f"  {g['date']}  {matchup(g):12}  {g['home']} {home_votes}, {g['away']} {100 - home_votes}")


def score():
    games, _, _ = load_games()
    total_right = {}
    total_games = 0
    for date, header, rows in saved_picks():
        winners = {}
        for m in header[2:]:
            away, home = m.split(" at ")
            result = next((g for g in games if g["date"] >= date
                           and g["home"] == home and g["away"] == away), None)
            if result and result["margin"] != 0:
                winners[m] = home if result["margin"] > 0 else away
        if not winners:
            print(f"{date}: no results yet")
            continue
        columns = {m: header.index(m) for m in winners}
        print(f"{date}: {len(winners)} of {len(header) - 2} games finished")
        for m, w in winners.items():
            right = sum(r[columns[m]] == w for r in rows)
            print(f"  {m:12}  winner {w:4} {right:3} of 100 right")
        total_games += len(winners)
        for r in rows:
            right = sum(r[columns[m]] == w for m, w in winners.items())
            total_right[int(r[0])] = total_right.get(int(r[0]), 0) + right

    if not total_games:
        return
    counts = game_counts(len(games))
    os.makedirs(os.path.dirname(SCOREBOARD_FILE), exist_ok=True)
    with open(SCOREBOARD_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["predictor", "games_learned_from_now", "right", "games_scored", "percent"])
        for p in sorted(total_right):
            writer.writerow([p, counts[p - 1], total_right[p], total_games,
                             f"{100 * total_right[p] / total_games:.1f}"])
    best = max(total_right.values())
    leaders = [p for p, r in total_right.items() if r == best]
    average = sum(total_right.values()) / len(total_right)
    print(f"\nSeason so far: {total_games} games scored. Average predictor: "
          f"{average:.1f} right. Best: {best} right (predictor "
          f"{', '.join(map(str, leaders))}).")
    print(f"Full scoreboard: {os.path.relpath(SCOREBOARD_FILE)}")


def build_website():
    sys.path.insert(0, os.path.join(HERE, "website"))
    import build
    build.main()


if __name__ == "__main__":
    commands = {"update": update, "pick": pick, "score": score}
    if len(sys.argv) != 2 or sys.argv[1] not in commands:
        print(__doc__.strip())
        sys.exit(1)
    commands[sys.argv[1]]()
    if sys.argv[1] in ("pick", "score"):
        build_website()

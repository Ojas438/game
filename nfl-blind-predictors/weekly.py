"""The weekly routine: update the data, lock in picks, and score them.

Usage:
    python weekly.py update   # download the latest scores, trades and player data
    python weekly.py pick     # save all 100 predictors' picks for the next week
    python weekly.py pick --skip "PHI at DAL"   # leave out a game already underway
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
import gzip
import io
import os
import sys
import urllib.request

from data import FEATURES, GAMES_FILE, SNAPS_FILE, TRADES_FILE, load_games, recent
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
    players = update_snaps()
    print(f"Updated: {games} games, {trades} trade records, {players} player-game records.")


def update_snaps():
    """Replace this season's player snap counts with the latest ones."""
    with open(GAMES_FILE, newline="") as f:
        season = max(int(r["season"]) for r in csv.DictReader(f))
    url = ("https://github.com/nflverse/nflverse-data/releases/download/"
           f"snap_counts/snap_counts_{season}.csv")
    with urllib.request.urlopen(url) as response:
        new = list(csv.DictReader(io.StringIO(response.read().decode("utf-8"))))
    with gzip.open(SNAPS_FILE, "rt", newline="") as f:
        kept = [r for r in csv.DictReader(f) if not r["game_id"].startswith(f"{season}_")]
    for r in new:
        snaps = int(float(r["offense_snaps"] or 0)) + int(float(r["defense_snaps"] or 0))
        if snaps > 0:
            kept.append({"game_id": r["game_id"], "team": r["team"],
                         "player_id": r["pfr_player_id"], "snaps": snaps})
    with gzip.open(SNAPS_FILE, "wt", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["game_id", "team", "player_id", "snaps"])
        writer.writeheader()
        writer.writerows(kept)
    return len(kept)


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


def pick(skip=()):
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
               if (g["season"], g["week"]) == week and matchup(g) not in already_matchups
               and matchup(g) not in skip]
    if not to_pick:
        print("Every game this week has already been picked.")
        return

    games = recent(games, upcoming[0]["season"])
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


# Picks saved before this date (weeks 8-10) were redone with version 2 after
# the games were played (see redo_version2.py), so they are scored separately
# from the live picks.
LIVE_FROM = "2026-11-17"


def score():
    games, upcoming, _ = load_games()
    right = {"v1": {}, "v2": {}}
    scored = {"v1": 0, "v2": 0}
    for date, header, rows in saved_picks():
        version = "v2" if date >= LIVE_FROM else "v1"
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
        label = "live" if version == "v2" else "redone after the games"
        print(f"{date} ({label}): {len(winners)} of {len(header) - 2} games finished")
        for m, w in winners.items():
            count = sum(r[columns[m]] == w for r in rows)
            print(f"  {m:12}  winner {w:4} {count:3} of 100 right")
        scored[version] += len(winners)
        for r in rows:
            got = sum(r[columns[m]] == w for m, w in winners.items())
            right[version][int(r[0])] = right[version].get(int(r[0]), 0) + got

    total_games = scored["v1"] + scored["v2"]
    if not total_games:
        return
    season = upcoming[0]["season"] if upcoming else games[-1]["season"]
    counts = game_counts(len(recent(games, season)))
    os.makedirs(os.path.dirname(SCOREBOARD_FILE), exist_ok=True)
    with open(SCOREBOARD_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["predictor", "games_learned_from_now", "right", "games_scored", "percent",
                         "right_v1", "games_scored_v1", "right_v2", "games_scored_v2"])
        for p in range(1, len(counts) + 1):
            r1, r2 = right["v1"].get(p, 0), right["v2"].get(p, 0)
            writer.writerow([p, counts[p - 1], r1 + r2, total_games,
                             f"{100 * (r1 + r2) / total_games:.1f}",
                             r1, scored["v1"], r2, scored["v2"]])
    print()
    for version, name in (("v1", "Weeks 8-10 (redone after the games)"), ("v2", "Week 11 on (live)")):
        if not scored[version]:
            continue
        best = max(right[version].values())
        leaders = [p for p, r in right[version].items() if r == best]
        average = sum(right[version].values()) / len(right[version])
        who = (f"predictor {', '.join(map(str, leaders))}" if len(leaders) <= 8
               else f"{len(leaders)} predictors tied")
        print(f"{name}: {scored[version]} games scored. Average predictor: "
              f"{average:.1f} right. Best: {best} right ({who}).")
    print(f"Full scoreboard: {os.path.relpath(SCOREBOARD_FILE)}")


def build_website():
    sys.path.insert(0, os.path.join(HERE, "website"))
    import build
    build.main()


if __name__ == "__main__":
    commands = {"update": update, "pick": pick, "score": score}
    if len(sys.argv) < 2 or sys.argv[1] not in commands:
        print(__doc__.strip())
        sys.exit(1)
    if sys.argv[1] == "pick" and sys.argv[2:3] == ["--skip"]:
        pick(skip=set(sys.argv[3:]))
    else:
        commands[sys.argv[1]]()
    if sys.argv[1] in ("pick", "score"):
        build_website()

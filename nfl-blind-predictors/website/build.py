"""Build website/index.html from template.html and data/games.csv.

Usage:
    python website/build.py
"""

import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from experiment import DATA_FILE, load_games  # noqa: E402
from predictors import team_name  # noqa: E402


def upcoming_games():
    """The games in the next week that hasn't been played yet."""
    with open(DATA_FILE, newline="") as f:
        unplayed = [r for r in csv.DictReader(f) if not r["home_score"]]
    if not unplayed:
        return []
    week = (unplayed[0]["season"], unplayed[0]["week"])
    return [
        [r["gameday"], team_name(r["home_team"]), team_name(r["away_team"])]
        for r in unplayed
        if (r["season"], r["week"]) == week
    ]


def main():
    games = load_games()
    teams = sorted({g["home"] for g in games} | {g["away"] for g in games})
    index = {t: i for i, t in enumerate(teams)}
    rows = ";".join(
        f"{index[g['home']]},{index[g['away']]},{g['margin']},{int(g['neutral'])}"
        for g in games
    )
    data = (
        f"const TEAMS = {json.dumps(teams)};\n"
        f"const UPCOMING = {json.dumps(upcoming_games())};\n"
        f"const GAME_ROWS = \"{rows}\";"
    )
    with open(os.path.join(HERE, "template.html")) as f:
        page = f.read().replace("/*__DATA__*/", data)
    with open(os.path.join(HERE, "index.html"), "w") as f:
        f.write(page)
    print(f"Wrote website/index.html ({len(games)} games)")


if __name__ == "__main__":
    main()

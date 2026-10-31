"""Build website/index.html from template.html and data/games.csv.

Usage:
    python website/build.py
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from experiment import TEST_SEASONS, load_games  # noqa: E402


def main():
    games = load_games()
    teams = sorted({g["home"] for g in games} | {g["away"] for g in games})
    index = {t: i for i, t in enumerate(teams)}
    rows = ";".join(
        f"{g['season']},{index[g['home']]},{index[g['away']]},{g['margin']},"
        f"{int(g['neutral'])},{'' if g['spread'] is None else format(g['spread'], 'g')}"
        for g in games
    )
    data = (
        f"const TEAMS = {json.dumps(teams)};\n"
        f"const TEST_SEASONS = {json.dumps(TEST_SEASONS)};\n"
        f"const GAME_ROWS = \"{rows}\";"
    )
    with open(os.path.join(HERE, "template.html")) as f:
        page = f.read().replace("/*__DATA__*/", data)
    with open(os.path.join(HERE, "index.html"), "w") as f:
        f.write(page)
    print(f"Wrote website/index.html ({len(games)} games)")


if __name__ == "__main__":
    main()

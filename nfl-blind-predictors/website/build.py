"""Build website/index.html from template.html and the files in data/.

Usage:
    python website/build.py
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from data import FEATURES, load_games  # noqa: E402


def main():
    games, upcoming, tracker = load_games()
    teams = sorted({g["home"] for g in games} | {g["away"] for g in games})
    index = {t: i for i, t in enumerate(teams)}

    def numbers(features):
        return ",".join(format(round(x, 4), "g") for x in features)

    rows = ";".join(
        f"{index[g['home']]},{index[g['away']]},{g['margin']},{int(g['neutral'])},"
        + numbers(g["features"])
        for g in games
    )
    # The next week on the schedule that hasn't been played.
    next_week = [
        [g["date"], g["home"], g["away"], int(g["neutral"])]
        for g in upcoming
        if (g["season"], g["week"]) == (upcoming[0]["season"], upcoming[0]["week"])
    ] if upcoming else []
    current = {
        team: {**tracker.features(team), "wins_losses": tracker.record_text(team)}
        for team in sorted(tracker.results)
    }
    data = (
        f"const TEAMS = {json.dumps(teams)};\n"
        f"const FEATURES = {json.dumps(FEATURES)};\n"
        f"const UPCOMING = {json.dumps(next_week)};\n"
        f"const CURRENT = {json.dumps(current)};\n"
        f"const GAME_ROWS = \"{rows}\";"
    )
    with open(os.path.join(HERE, "template.html")) as f:
        page = f.read().replace("/*__DATA__*/", data)
    with open(os.path.join(HERE, "index.html"), "w") as f:
        f.write(page)
    print(f"Wrote website/index.html ({len(games)} games, {len(next_week)} upcoming)")


if __name__ == "__main__":
    main()

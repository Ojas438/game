"""Load NFL games and work out what each team looked like before every game.

For every game, each team gets four numbers, using only what was known
before kickoff:

- record: this season's win rate so far (0 means .500, +0.5 means unbeaten)
- trend:  average point margin over its last 3 games this season
- draft:  how high it picked in this year's draft (each top-100 pick counts,
          the 1st pick is worth 1.0 and the 100th is worth 0.01)
- trades: players gained minus players given away in trades this year
"""

import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
GAMES_FILE = os.path.join(HERE, "data", "games.csv")
DRAFT_FILE = os.path.join(HERE, "data", "draft_picks.csv")
TRADES_FILE = os.path.join(HERE, "data", "trades.csv")

FEATURES = ["record", "trend", "draft", "trades"]
TREND_GAMES = 3

# Teams that moved cities count as the same team, and the draft file uses
# different abbreviations for some teams.
TEAM_CODES = {
    "OAK": "LV", "SD": "LAC", "STL": "LA",
    "GNB": "GB", "KAN": "KC", "LAR": "LA", "LVR": "LV", "NOR": "NO",
    "NWE": "NE", "SDG": "LAC", "SFO": "SF", "TAM": "TB",
}


def team_name(code):
    return TEAM_CODES.get(code, code)


def load_draft_scores():
    scores = {}
    with open(DRAFT_FILE, newline="") as f:
        for row in csv.DictReader(f):
            key = (int(row["season"]), team_name(row["team"]))
            value = max(0.0, 1 - (int(row["pick"]) - 1) / 100)
            scores[key] = scores.get(key, 0.0) + value
    return scores


def load_player_trades():
    """Every player moved in a trade, as (date, season, team that got him, team that gave him)."""
    moves = []
    with open(TRADES_FILE, newline="") as f:
        for row in csv.DictReader(f):
            if row["player"] and not row["pick_season"]:
                moves.append((row["trade_date"], int(row["season"]),
                              team_name(row["received"]), team_name(row["gave"])))
    moves.sort()
    return moves


class TeamTracker:
    """Keeps each team's record, recent margins, draft and trades up to a date."""

    def __init__(self):
        self.draft = load_draft_scores()
        self.trade_moves = load_player_trades()
        self.next_trade = 0
        self.season = None
        self.results = {}  # team -> list of point margins this season
        self.trades = {}   # team -> players in minus players out this season

    def advance_to(self, season, date):
        if season != self.season:
            self.season = season
            self.results = {}
            self.trades = {}
        while (self.next_trade < len(self.trade_moves)
               and self.trade_moves[self.next_trade][0] < date):
            _, trade_season, got, gave = self.trade_moves[self.next_trade]
            if trade_season == season:
                self.trades[got] = self.trades.get(got, 0) + 1
                self.trades[gave] = self.trades.get(gave, 0) - 1
            self.next_trade += 1

    def features(self, team):
        margins = self.results.get(team, [])
        wins = sum(1 if m > 0 else 0.5 if m == 0 else 0 for m in margins)
        recent = margins[-TREND_GAMES:]
        return {
            "record": (wins + 1) / (len(margins) + 2) - 0.5,
            "trend": sum(recent) / len(recent) if recent else 0.0,
            "draft": self.draft.get((self.season, team), 0.0),
            "trades": self.trades.get(team, 0),
        }

    def record_text(self, team):
        margins = self.results.get(team, [])
        wins = sum(m > 0 for m in margins)
        losses = sum(m < 0 for m in margins)
        ties = len(margins) - wins - losses
        return f"{wins}-{losses}" + (f"-{ties}" if ties else "")

    def add_result(self, home, away, margin):
        self.results.setdefault(home, []).append(margin)
        self.results.setdefault(away, []).append(-margin)


def load_games():
    """Return (finished games, upcoming games, tracker as of today), oldest first.

    Each game has home, away, margin (None if not played yet), neutral,
    and features: home team's numbers minus away team's, in FEATURES order.
    """
    with open(GAMES_FILE, newline="") as f:
        rows = sorted(csv.DictReader(f), key=lambda r: r["gameday"])

    tracker = TeamTracker()
    finished, upcoming = [], []
    for row in rows:
        season = int(row["season"])
        home, away = team_name(row["home_team"]), team_name(row["away_team"])
        played = row["home_score"] != ""
        tracker.advance_to(season, row["gameday"])
        home_f, away_f = tracker.features(home), tracker.features(away)
        game = {
            "season": season,
            "week": row["week"],
            "date": row["gameday"],
            "home": home,
            "away": away,
            "neutral": row["location"] == "Neutral",
            "margin": int(row["home_score"]) - int(row["away_score"]) if played else None,
            "spread": float(row["spread_line"]) if row["spread_line"] else None,
            "features": [home_f[k] - away_f[k] for k in FEATURES],
        }
        if played:
            finished.append(game)
            tracker.add_result(home, away, game["margin"])
        else:
            upcoming.append(game)
    return finished, upcoming, tracker

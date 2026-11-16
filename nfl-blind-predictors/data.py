"""Load NFL games and work out what each team looked like before every game.

For every game, each team gets four numbers, using only what was known
before kickoff:

- record: this season's win rate so far (0 means .500, +0.5 means unbeaten)
- trend:  average point margin over its last 3 games this season
- draft:  how high it picked in this year's draft (each top-100 pick counts,
          the 1st pick is worth 1.0 and the 100th is worth 0.01)
- trades: players gained minus players given away in trades this year
- roster: how good the players who played in the team's last game are.
          Each player is rated by his teams' average point margin over his
          last 17 games (on any team), and the team's number is the average
          of its players' ratings, weighted by how many plays each was on the
          field for. Player data starts in 2013, and a team's first game of a
          season has no roster number yet.
"""

import csv
import gzip
import os
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
GAMES_FILE = os.path.join(HERE, "data", "games.csv")
DRAFT_FILE = os.path.join(HERE, "data", "draft_picks.csv")
TRADES_FILE = os.path.join(HERE, "data", "trades.csv")
SNAPS_FILE = os.path.join(HERE, "data", "snap_counts.csv.gz")

FEATURES = ["record", "trend", "draft", "trades", "roster"]
TREND_GAMES = 3
PLAYER_GAMES = 17
# A player's rating is pulled toward 0 as if he had also played this many
# average games, so one big game doesn't make him look great.
PLAYER_PRIOR_GAMES = 3

# Teams that moved cities count as the same team, and the draft file uses
# different abbreviations for some teams.
TEAM_CODES = {
    "OAK": "LV", "SD": "LAC", "STL": "LA",
    "GNB": "GB", "KAN": "KC", "LAR": "LA", "LVR": "LV", "NOR": "NO",
    "NWE": "NE", "SDG": "LAC", "SFO": "SF", "TAM": "TB",
}


# Predictors only learn from this many seasons before the one being predicted
# (plus that season's earlier games). For 2026 that means 2020 and later.
RECENT_SEASONS = 6


def recent(games, season):
    """The games a predictor may learn from when predicting `season`."""
    return [g for g in games if season - RECENT_SEASONS <= g["season"] <= season]


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


def load_snaps():
    """Who played in each game: game id -> list of (team, player id, snaps)."""
    snaps = {}
    with gzip.open(SNAPS_FILE, "rt", newline="") as f:
        for row in csv.DictReader(f):
            snaps.setdefault(row["game_id"], []).append(
                (team_name(row["team"]), row["player_id"], int(row["snaps"])))
    return snaps


class TeamTracker:
    """Keeps each team's record, recent margins, draft, trades and roster up to a date."""

    def __init__(self):
        self.draft = load_draft_scores()
        self.trade_moves = load_player_trades()
        self.snaps = load_snaps()
        self.next_trade = 0
        self.season = None
        self.results = {}  # team -> list of point margins this season
        self.trades = {}   # team -> players in minus players out this season
        self.players = {}  # player id -> his teams' margins in his last games
        self.lineups = {}  # team -> {player id: snaps} in its last game this season

    def advance_to(self, season, date):
        if season != self.season:
            self.season = season
            self.results = {}
            self.trades = {}
            self.lineups = {}
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
            "roster": self.roster_strength(team),
        }

    def player_rating(self, player):
        margins = self.players.get(player, ())
        return sum(margins) / (len(margins) + PLAYER_PRIOR_GAMES)

    def roster_strength(self, team):
        lineup = self.lineups.get(team)
        if not lineup:
            return 0.0
        total_snaps = sum(lineup.values())
        return sum(snaps * self.player_rating(p) for p, snaps in lineup.items()) / total_snaps

    def record_text(self, team):
        margins = self.results.get(team, [])
        wins = sum(m > 0 for m in margins)
        losses = sum(m < 0 for m in margins)
        ties = len(margins) - wins - losses
        return f"{wins}-{losses}" + (f"-{ties}" if ties else "")

    def add_result(self, home, away, margin, game_id=None):
        self.results.setdefault(home, []).append(margin)
        self.results.setdefault(away, []).append(-margin)
        played = self.snaps.get(game_id)
        if not played:
            return
        lineups = {home: {}, away: {}}
        for team, player, snaps in played:
            if team in lineups:
                lineups[team][player] = snaps
                history = self.players.setdefault(player, deque(maxlen=PLAYER_GAMES))
                history.append(margin if team == home else -margin)
        self.lineups.update(lineups)


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
            game_id = f"{season}_{int(row['week']):02d}_{row['away_team']}_{row['home_team']}"
            tracker.add_result(home, away, game["margin"], game_id)
        else:
            upcoming.append(game)
    return finished, upcoming, tracker

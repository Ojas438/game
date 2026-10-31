"""100 identical NFL game predictors.

Every predictor runs the exact same code. The only thing that can differ
between them is how many past games they are allowed to learn from.

How a predictor works: it predicts the home team's winning margin as

    home rating - away rating + home-field bonus
    + record weight * (home record - away record)
    + trend weight  * (home trend  - away trend)
    + draft weight  * (home draft  - away draft)
    + trades weight * (home trades - away trades)

(see data.py for what record, trend, draft and trades mean). Learning means
adjusting the team ratings, the home bonus and the four weights until that
formula matches the real score margins of the games it was shown as closely
as possible. A predictor shown zero games has everything at 0, so it can
only guess.
"""

import random

from data import FEATURES

NUM_PREDICTORS = 100

# How strongly everything is pulled toward 0 when there are few games.
# It acts like every team already played this many perfectly average games.
PRIOR_GAMES = 3.0
TRAINING_PASSES = 30


class Predictor:
    def __init__(self, predictor_id, seed=0):
        self.predictor_id = predictor_id
        self.ratings = {}
        self.home_bonus = 0.0
        self.weights = [0.0] * len(FEATURES)
        self.games_seen = 0
        # Breaks exact ties (always the case with no data) by a coin flip.
        self._rng = random.Random(seed * 1000 + predictor_id)

    def _extras(self, game):
        """The part of the predicted margin that comes from the four numbers."""
        return sum(w * x for w, x in zip(self.weights, game["features"]))

    def train(self, games):
        """Learn from a list of finished games."""
        self.games_seen = len(games)
        self.ratings = {}
        self.home_bonus = 0.0
        self.weights = [0.0] * len(FEATURES)
        games_by_team = {}
        for game in games:
            games_by_team.setdefault(game["home"], []).append(game)
            games_by_team.setdefault(game["away"], []).append(game)
            self.ratings.setdefault(game["home"], 0.0)
            self.ratings.setdefault(game["away"], 0.0)
        home_games = [g for g in games if not g["neutral"]]
        # Pull each weight toward 0 as if there were PRIOR_GAMES typical games
        # where it didn't matter.
        weight_prior = [
            PRIOR_GAMES * sum(g["features"][k] ** 2 for g in games) / len(games)
            if games else 0.0
            for k in range(len(FEATURES))
        ]

        for _ in range(TRAINING_PASSES):
            for team, team_games in games_by_team.items():
                total = 0.0
                for g in team_games:
                    bonus = 0.0 if g["neutral"] else self.home_bonus
                    rest = g["margin"] - bonus - self._extras(g)
                    if g["home"] == team:
                        total += rest + self.ratings[g["away"]]
                    else:
                        total += -rest + self.ratings[g["home"]]
                self.ratings[team] = total / (len(team_games) + PRIOR_GAMES)

            total = sum(
                g["margin"] - self.ratings[g["home"]] + self.ratings[g["away"]]
                - self._extras(g)
                for g in home_games
            )
            self.home_bonus = total / (len(home_games) + PRIOR_GAMES)

            for k in range(len(FEATURES)):
                top = bottom = 0.0
                for g in games:
                    x = g["features"][k]
                    if x == 0:
                        continue
                    bonus = 0.0 if g["neutral"] else self.home_bonus
                    others = self._extras(g) - self.weights[k] * x
                    rest = (g["margin"] - self.ratings[g["home"]]
                            + self.ratings[g["away"]] - bonus - others)
                    top += x * rest
                    bottom += x * x
                if bottom:
                    self.weights[k] = top / (bottom + weight_prior[k])

    def predicted_margin(self, home, away, features, neutral=False):
        bonus = 0.0 if neutral else self.home_bonus
        return (self.ratings.get(home, 0.0) - self.ratings.get(away, 0.0) + bonus
                + sum(w * x for w, x in zip(self.weights, features)))

    def predict(self, home, away, features, neutral=False):
        """Return the team this predictor thinks will win."""
        margin = self.predicted_margin(home, away, features, neutral)
        if margin == 0:
            return self._rng.choice([home, away])
        return home if margin > 0 else away


def build_predictors(count=NUM_PREDICTORS, seed=0):
    return [Predictor(i + 1, seed) for i in range(count)]


def game_counts(max_games, count=NUM_PREDICTORS):
    """How many games each predictor gets: 0 for the first, max_games for the last.

    The counts grow by roughly the same percentage each step (1, 2, 3, 4, 5,
    6, 7, 8, 9, 10, 11, 13, 14 ... thousands), so there are lots of
    predictors in the small range where each extra game matters most.
    """
    counts = [0]
    for i in range(1, count):
        target = round(max_games ** ((i - 1) / (count - 2)))
        counts.append(max(target, counts[-1] + 1))
    counts[-1] = max_games
    return counts

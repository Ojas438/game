"""100 identical NFL game predictors that are given no data.

Every predictor runs the exact same code. None of them sees standings,
records, injuries, odds, or past results. The only thing a predictor is
told is which two teams are playing, and it has to pick a winner anyway.
"""

import random

NUM_PREDICTORS = 100


class BlindPredictor:
    """Picks NFL winners with zero information about the teams."""

    def __init__(self, predictor_id):
        self.predictor_id = predictor_id
        # Each predictor gets its own random number generator, seeded from the
        # operating system. That is the only thing that differs between them.
        self._rng = random.Random()

    def predict(self, home_team, away_team):
        """Return a pick for one game: winner, final score, and confidence."""
        winner = self._rng.choice([home_team, away_team])
        loser = away_team if winner == home_team else home_team
        winning_score = self._rng.randint(10, 41)
        losing_score = self._rng.randint(3, winning_score - 1)
        return {
            "predictor": self.predictor_id,
            "winner": winner,
            "loser": loser,
            "score": f"{winning_score}-{losing_score}",
            "confidence": round(self._rng.uniform(0.5, 1.0), 2),
        }


def build_predictors(count=NUM_PREDICTORS):
    return [BlindPredictor(i + 1) for i in range(count)]

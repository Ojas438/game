# NFL Predictors: How Much Data Is Enough?

A science project about whether AI training could use less data (and so less
computing power, electricity, and water for cooling data centers) without
getting worse.

There are 100 predictors, and they all run the exact same code. The only
difference is how many past NFL games each one is allowed to learn from:

- Predictor 1 gets **0 games**, so it can only guess.
- Predictor 100 gets **every game available** (about 5,800).
- The ones in between get amounts that grow step by step (1, 2, 3 ... 100,
  119, 142 ... 1,000 ... 5,000), with more predictors at the small end,
  where each extra game should matter most.

Before every game, each predictor looks at four things about both teams,
using only what was known before kickoff:

- **Record:** this season's win-loss record so far.
- **Trend:** average point margin over the team's last 3 games.
- **Draft:** how high the team picked in this year's draft.
- **Trades:** players gained minus players given away in trades this year.

It also gives every team a strength rating and adds a home-field bonus. From
the games it was shown, it learns the ratings, the bonus, and how much each of
the four things matters, then picks winners.

## The test

Each predictor is tested on seasons it never saw: 2021, 2022, 2023, 2024 and
2025 (1,420 games). For each test season it learns from the N most recent
games played before that season started.

## Run it

```bash
python experiment.py
```

Prints the accuracy of all 100 predictors and saves them to
`results/results.csv`, with the change from one predictor to the next and the
training time. Needs Python 3, no packages. Takes a few seconds.

To have all 100 vote on an upcoming game:

```bash
python predict.py KC BUF
```

## Website

`website/index.html` shows what all 100 predictors pick for upcoming games.
It starts with the next week on the schedule. You can change, remove, or add
games, and copy every pick to paste into a spreadsheet. Each predictor learns
from the most recent finished games. Open it in a browser, or rebuild it after
updating `data/games.csv`:

```bash
python website/build.py
```

## Results

| Predictor | Games learned from | Accuracy |
| --- | --- | --- |
| 1 | 0 | 50.4% |
| 11 | 10 | 52.7% |
| 50 | 70 | 57.3% |
| 60 | 170 | 58.8% |
| 72 | 491 | 61.1% |
| 78 | 835 (best) | 61.8% |
| 85 | 1,551 | 59.8% |
| 100 | 5,852 | 60.9% |
| Betting favorites | (for comparison) | 66.5% |

What happened:

1. **The first few hundred games give almost all the gain.** Going from 0 to
   491 games (about two seasons) takes accuracy from a coin flip to 61%,
   within 1 point of the best.
2. **After about 800 games, more data stopped helping.** The predictor with
   all ~5,800 games was no better than the one with 835, and took about 8
   times longer to train.

So for this problem, about 8 to 15% of the data gave as good a result as all
of it. Training on the rest cost extra computing (and water) for no gain.

An earlier version only used final scores, with no record, trend, draft or
trade information. That one peaked at 61.2% with 344 games and then got
worse with more data (57.0% with all of it), because games from 10 or 20
years ago describe teams that have completely changed. Record and trend
describe how a team is doing *this season*, so old games stay useful for
learning how much those matter.

## Limits

- Each accuracy has a margin of error of about +/-2.6 points, because 1,420
  test games is still a fairly small sample. Small ups and downs between
  neighboring predictors are mostly luck; look at the overall shape of the
  curve, not single steps.
- This is a tiny model. Large AI models behave differently, but the same
  question (where does more data stop helping?) is studied for them too.
- Training time here is fractions of a second. It's used as a stand-in for
  the computing cost, not a real measurement of water use.

## Data

All from [nflverse](https://github.com/nflverse/nfldata):

- `data/games.csv`: every NFL game since 1999, plus this season's schedule.
- `data/draft_picks.csv`: every draft pick since 1999, through the 2026 draft.
- `data/trades.csv`: every trade since 2002. The file only goes up to
  April 2026, so trades made during this season aren't in it yet.

Teams that moved (Oakland, San Diego, St. Louis) count as the same team after
the move.

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

Each predictor gives every team a strength rating plus a home-field bonus,
fitted to the score margins of the games it was shown, then picks winners.

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

`website/index.html` runs the same algorithm in a web browser. It shows the
results chart, lets you try any of the 100 predictors on a matchup, and shows
the algorithm's code. Open it in a browser, or rebuild it after changing the
data or template:

```bash
python website/build.py
```

The website flips its own coins, so the no-data predictor's score there
(54.0%) differs from the Python version's (50.4%). Both are coin-flip luck.
Every other predictor gets the same score in both.

## Results

| Predictor | Games learned from | Accuracy |
| --- | --- | --- |
| 1 | 0 | 50.4% |
| 11 | 10 | 55.3% |
| 50 | 70 | 57.1% |
| 60 | 170 | 60.7% |
| 68 | 344 (best) | 61.2% |
| 80 | 996 | 57.4% |
| 100 | 5,852 | 57.0% |
| Betting favorites | (for comparison) | 66.5% |

What happened:

1. **The first few games give the biggest jump.** Going from 0 to about 10
   games takes accuracy from a coin flip to about 55%.
2. **Gains get smaller and stop at a few hundred games** (one to two seasons).
   170 games was already within 1 point of the best.
3. **More data after that made it worse.** Games from 10 or 20 years ago
   describe teams that no longer exist in that form, so they teach the
   predictor wrong things. The predictor with all ~5,800 games was 4 points
   worse than the one with 344, and took about 50 times longer to train.

So for this problem, about 3% of the data gave the best result. Training on
the rest cost extra computing (and water) and made the answer worse. The
right *amount* and *freshness* of data mattered more than having the most.

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

`data/games.csv` holds every NFL game since 1999, from
[nflverse](https://github.com/nflverse/nfldata). Teams that moved
(Oakland, San Diego, St. Louis) count as the same team after the move.

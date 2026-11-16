# NFL Predictors: How Much Data Is Enough?

A science project about whether AI training could use less data (and so less
computing power, electricity, and water for cooling data centers) without
getting worse.

There are 100 predictors, and they all run the exact same code. The only
difference is how many past NFL games each one is allowed to learn from:

- Predictor 1 gets **0 games**, so it can only guess.
- Predictor 100 gets **every game from the 6 seasons before** the season it
  predicts (for 2026, every game since the 2020 season), plus that season's
  earlier games.
- The ones in between get amounts that grow step by step, with more
  predictors at the small end, where each extra game should matter most.

Before every game, each predictor looks at five things about both teams,
using only what was known before kickoff:

- **Record:** this season's win-loss record so far.
- **Trend:** average point margin over the team's last 3 games.
- **Draft:** how high the team picked in this year's draft.
- **Trades:** players gained minus players given away in trades this year.
- **Roster:** how good the players who played in the team's last game are.
  Each player is rated by how his teams did in his last 17 games, on any
  team, so a player who changes teams brings his rating with him.

It also gives every team a strength rating and adds a home-field bonus. From
the games it was shown, it learns the ratings, the bonus, and how much each of
the five things matters, then picks winners.

This is version 2. Version 1 learned from every game since 1999 and had no
roster stat. Weeks 8 to 10 of 2026 were first picked live with version 1,
then redone with version 2 after those games were played (`python
redo_version2.py`), using only data from before each original pick date.
Those redone picks are a re-test, not live predictions, so they're scored
separately. Live version 2 picks start with week 11. The original version 1
picks are kept in `picks/version1/`.

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

## Weekly routine

Before the first game of each week (usually Thursday):

```bash
python weekly.py update
```

```bash
python weekly.py pick
```

This downloads the latest scores and trades, then saves all 100 predictors'
picks to `picks/<date>.csv`. Saved picks are never changed.

After the games:

```bash
python weekly.py update
```

```bash
python weekly.py score
```

This scores every saved pick and writes the season totals to
`results/season_scoreboard.csv`.

## Website

`website/index.html` shows what all 100 predictors pick for upcoming games.
It starts with every game from today through Friday. You can change, remove, or add
games, and copy every pick to paste into a spreadsheet. Each predictor learns
from the most recent finished games. Open it in a browser, or rebuild it after
updating `data/games.csv`:

```bash
python website/build.py
```

## Results

Version 2, tested on 1,420 games from 2021 to 2025:

| Predictor | Games learned from | Accuracy |
| --- | --- | --- |
| 1 | 0 | 50.4% |
| 11 | 10 | 53.1% |
| 30 | 29 | 57.8% |
| 70 | 168 | 59.3% |
| 80 | 356 | 59.9% |
| 90 | 755 | 60.8% |
| 93 | 947 (best) | 62.5% |
| 100 | 1,604 (all) | 62.3% |
| Betting favorites | (for comparison) | 66.5% |

1. **Accuracy kept rising up to about 900 games** (about 3.5 seasons), then
   leveled off. Using all 1,604 games was no better than 947.
2. **Recent data didn't make it worse.** Version 1, which learned from every
   game since 1999, peaked at 61.8% with 835 games and was 60.9% with all
   5,852. Version 2 is slightly better at 62.5%, but the difference is
   inside the margin of error.

Version 1 results (every game since 1999, no roster stat):

| Predictor | Games learned from | Accuracy |
| --- | --- | --- |
| 1 | 0 | 50.4% |
| 50 | 70 | 57.3% |
| 72 | 491 | 61.1% |
| 78 | 835 (best) | 61.8% |
| 85 | 1,551 | 59.8% |
| 100 | 5,852 | 60.9% |

An even earlier version used only final scores. It peaked at 61.2% with 344
games and then got worse with more data (57.0% with all of it), because games
from 10 or 20 years ago describe teams that have completely changed.

## Which kind of data matters?

```bash
python ablation.py
```

Runs the version 2 test seven times: with all stats, with scores only, and
with each stat left out. Average accuracy over the predictors in each range:

| Version | 1 to 100 games | 100 to 500 games | 500+ games |
| --- | --- | --- | --- |
| All stats | 55.5% | 58.8% | 61.3% |
| Scores only | 55.6% | 59.5% | 58.6% |
| No record | 55.4% | 58.7% | 61.3% |
| No trend | 56.9% | 59.1% | 61.3% |
| No draft | 55.9% | 59.7% | 61.3% |
| No trades | 55.5% | 58.8% | 61.4% |
| No roster | 55.2% | 58.6% | 60.5% |

- **Roster matters most.** Leaving it out lowers accuracy with all 1,604
  games from 62.3% to 60.0%.
- **Record and trend barely matter once roster is there.** The roster stat
  already captures how well a team is playing.
- **Draft and trades made almost no difference.**
- With very little data, the extra stats don't help, because there are too
  many weights to learn from a few games.
- Most of these differences are under 1 point, within the margin of error.

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
- `data/snap_counts.csv.gz`: every player's plays on offense and defense in
  every game since 2013, used for the roster stat.

Teams that moved (Oakland, San Diego, St. Louis) count as the same team after
the move.

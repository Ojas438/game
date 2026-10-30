# NFL Blind Predictors

100 algorithms, all running identical code, all trying to predict NFL games,
and none of them given any data: no records, stats, injuries, odds, or past
results. Each one is told only which two teams are playing.

Each predictor has its own random number generator, and that's the only thing
that differs between them. Over many games, expect each one to be right about
50% of the time and the group vote to land close to 50/50.

## Run it

```bash
python predict.py Chiefs Bills
```

The first team is the home team. Needs Python 3, no packages.

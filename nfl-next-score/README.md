# 🏈 Who Scores Next? Predicting the Next Score in an NFL Game

**Research question:** Can a computer model use the game situation to predict *who* will score next and *how*, better than simple guessing?

This project uses every play from 8 NFL seasons (2018–2025). It teaches a computer to look at a game situation (where the ball is, the down, the score, the clock) and give the chance of each possible next score.

---

## The big idea, in plain English

Picture any moment in a football game. Before the half ends, one of 11 things will happen next:

| The team **with the ball** scores… | The **other team** scores… | Or… |
|---|---|---|
| Passing TD | Passing TD | **No Score** (the half ends first) |
| Rushing TD | Rushing TD | |
| Field Goal | Field Goal | |
| Safety | Safety | |
| Return TD | Return TD | |

("Return TD" means any touchdown that isn't a normal run or catch: kick or punt returns, interception returns, fumble returns.)

The computer studies about 284,000 real plays where we already know what happened next. It learns patterns, like "teams inside the 10-yard line usually score a touchdown" or "with 20 seconds left in the half, usually nobody scores." Then we test it on the 2025 season, which it has never seen, to check whether it learned real patterns or just memorized.

---

## The experiment

| Part | What it is in this project |
|---|---|
| **Independent variable** (what I changed) | Which game information the model gets, and in the last trial, which type of model |
| **Dependent variables** (what I measured) | Accuracy, log loss, and calibration error (explained below) |
| **Controls** (kept the same) | Same data, same training seasons (2018–2024), same test season (2025), same 11 outcomes, same scoring rules for every trial |
| **Baselines** (simple guessing to beat) | (1) Always guess the most common outcome. (2) Guess using only which team has the ball (home or away team) |

### Trials

1. **Baseline:** always guess the most common outcome ("Ball team: Field Goal")
2. **Field position only:** the model only knows the yard line
3. **Field position + down + distance**
4. **Everything:** adds score, time left, quarter, timeouts, and home/away (logistic regression model)
5. **Everything with a stronger model:** the same 10 inputs, but an XGBoost model

**Bonus fairness check:** I also gave the stronger XGBoost model only field position, and then field position + down + distance. That shows whether improvements come from *more information* or from a *fancier model*.

### How I measured "good"

- **Accuracy:** how often the model's #1 guess was exactly right. Higher is better. It's easy to understand, but it ignores how confident the model was.
- **Log loss:** a "surprise score." If the model said something had a 60% chance and it happened, it's barely surprised (small penalty). If it said 2% and that happened, it's very surprised (big penalty). We average the penalty over every play. **Lower is better.** This is the main measure, because it rewards honest percentages, not just lucky top guesses.
  - *Kid-friendly trick:* e raised to the log loss (e ≈ 2.718) tells you about how many outcomes the model is "stuck choosing between." The baseline's 1.897 is like being stuck between **6.7** equally likely outcomes. The best model's 1.579 is like **4.8**.
- **Calibration:** when the model says "30%," does it happen about 30% of the time? We check this with a calibration chart. The **calibration error** is the average gap. Smaller is better.

---

## Results (tested on all 40,516 plays from 285 games in the 2025 season)

| Trial | Inputs | Accuracy | Who-scores accuracy* | Log loss (lower = better) | Calibration error |
|---|---|---|---|---|---|
| 1. Always guess most common | none | 28.1% | 63.3% | 1.897 | 2.0% |
| Baseline 2: which team has ball | home/away | 28.1% | 63.3% | 1.897 | 2.0% |
| 2. Field position only | yard line | 28.1% | 61.6% | 1.827 | 2.6% |
| 3. + down & distance | 3 inputs | 28.2% | 63.3% | 1.805 | 2.0% |
| 4. Everything (logistic) | 10 inputs | 35.5% | 67.1% | 1.654 | 1.8% |
| **5. Everything (XGBoost)** | 10 inputs | **38.2%** | **69.0%** | **1.579** | **1.2%** |
| Bonus: XGBoost, field position only | yard line | 29.1% | 61.5% | 1.815 | 1.6% |
| Bonus: XGBoost, field + down + distance | 3 inputs | 29.9% | 62.2% | 1.787 | 1.1% |

\*Who-scores accuracy only checks *who* scores next (ball team, other team, or nobody), not *how*.

The best model beat simple guessing by about **10 percentage points** in accuracy (38.2% vs 28.1%). Its log loss was about **17% lower**. The "95% ranges" in `results/trial_results.csv` and the error bars on the graph show these differences are much bigger than luck could explain.

**Most important factors** (from the XGBoost model): the clock was #1, field position #2, then the score, then down & distance. Timeouts and home/away barely mattered.

See **[RESULTS_AND_CONCLUSION.md](RESULTS_AND_CONCLUSION.md)** for the full write-up for the display board, and **[JUDGE_QUESTIONS.md](JUDGE_QUESTIONS.md)** to practice for judging.

### Graphs (in the `graphs/` folder)

| File | What it shows |
|---|---|
| `1_trial_comparison.png` | Accuracy and log loss for every trial |
| `2_fairness_check.png` | More inputs helps more than a fancier model |
| `3_feature_importance.png` | Which game factors matter most |
| `3b_feature_importance_detail.png` | Same idea, each of the 10 inputs separately |
| `4_calibration.png` | When the model says X%, does it happen X% of the time? |
| `5_down_the_field.png` | How the chances change as a team drives down the field |

---

## How to run it yourself

You need Python 3.10 or newer. In a terminal, from this folder:

```bash
pip install -r requirements.txt
python 01_get_data.py        # download 8 seasons of plays (~1 minute)
python 02_make_labels.py     # label each play with the next score (~1 minute)
python 03_run_experiment.py  # run every trial and print the results table (~1 minute)
python 04_make_graphs.py     # make the PNG graphs
python 05_export_demo.py     # copy the best model into the web demo
node check_demo.js           # (optional, needs Node.js) check the web demo matches Python
```

Or run everything at once: `bash run_all.sh`

### What each file does

| File | Job |
|---|---|
| `01_get_data.py` | Downloads free play-by-play data from nflverse |
| `02_make_labels.py` | Looks ahead from each play to find the next score (the "answer key") |
| `03_run_experiment.py` | Trains and tests every trial and saves the results table |
| `04_make_graphs.py` | Makes the graphs for the display board |
| `05_export_demo.py` | Saves the best model in a format the web page can use |
| `check_demo.js` | Proves the web page gives the same numbers as Python |
| `demo/` | The web demo (open `index.html` through a web server, or deploy it to Vercel) |

---

## The web demo

The `demo/` folder is a website where anyone can enter a game situation and see the predicted chances as a bar chart. The model runs inside the visitor's web browser, so no server is needed.

**To try it on your own computer:** from inside the `demo` folder, run `python -m http.server 8000`, then open http://localhost:8000.

### Put it on the internet with Vercel (free)

1. Make sure this project is pushed to GitHub (it lives in the `nfl-next-score` folder of your repo).
2. Go to **https://vercel.com** and sign in with your GitHub account.
3. Click **Add New… → Project**.
4. Find your GitHub repository (`game`) in the list and click **Import**.
5. On the setup screen:
   - **Project Name:** something like `who-scores-next`
   - **Framework Preset:** choose **Other**
   - **Root Directory:** click **Edit** and choose `nfl-next-score/demo` ← *the most important step!*
   - Leave the Build Command and Output Directory empty.
6. Click **Deploy**. After about 30 seconds you get a link like `https://who-scores-next.vercel.app`.
7. Open the link and click the preset buttons ("Red zone", "Two-minute drill") to check it works.
8. **Bonus:** put the link on your board as a QR code (search "QR code generator") so judges can try it on their phones.

From now on, every time you push a change to GitHub, Vercel updates the website automatically.

> Ask a parent or teacher before creating accounts. Both GitHub and Vercel are free for this kind of project.

---

## Limitations (be honest about these, judges like it!)

- **The model doesn't know who is playing.** It treats the Chiefs and the worst team in the league the same. Adding team strength would probably help a lot.
- **Plays in the same drive are connected.** Ten plays from one drive all share the same answer, so the 40,516 test plays are not 40,516 independent tests. That's why the 95% ranges were computed by re-drawing whole *games*, not single plays.
- **Rare outcomes are hard.** Safeties and return TDs are less than 1–2% of answers, so the model rarely predicts them.
- **Overtime was left out** because it has different rules.
- **Football is random.** Fumbles, interceptions, and long returns are partly luck, so no model could be right every time.

## Ideas for future work

- Add **team strength** (like point spreads or season records).
- Add **weather** and **stadium** (dome or outdoors), or who the quarterback is.
- Try predicting **expected points** (a single number) instead of 11 categories.
- Test whether the model gets worse in **close, late-game** situations.
- Update the model live during a real game.

---

*Data: [nflverse](https://github.com/nflverse) play-by-play data, free and public, loaded with the `nflreadpy` Python package.*

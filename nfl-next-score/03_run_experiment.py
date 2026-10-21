"""
STEP 3: RUN THE EXPERIMENT (baselines + 4 model trials)

What this does, in plain English:
  - TRAIN on seasons 2018-2024 (the model "studies" these plays and their answers).
  - TEST on the 2025 season (plays the model has NEVER seen), so the test is fair.
  - Every trial uses the same data, the same test season, and the same 11 answers (controls).
  - The thing we change (independent variable) is WHICH INPUTS the model gets, and in
    the last trial, WHICH TYPE of model.
  - We measure (dependent variables):
        accuracy  = how often the model's top guess was exactly right
        log loss  = how "surprised" the model was by what really happened (LOWER is better)
        calibration error = when the model says "30%", how far off from 30% reality was

Run it with:   python 03_run_experiment.py
"""

import json

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

HOW = ["Passing TD", "Rushing TD", "Field Goal", "Safety", "Return TD"]
CLASSES = [f"Ball team: {h}" for h in HOW] + [f"Other team: {h}" for h in HOW] + ["No Score"]
TEST_SEASON = 2025

# The inputs ("features") each trial is allowed to see.
FIELD = ["yardline_100"]
FIELD_DOWN = FIELD + ["down", "ydstogo"]
EVERYTHING = FIELD_DOWN + [
    "score_differential", "half_seconds_remaining", "game_seconds_remaining", "qtr",
    "posteam_timeouts_remaining", "defteam_timeouts_remaining", "is_home",
]

plays = pd.read_parquet("data/plays_labeled.parquet")
plays = plays.dropna(subset=EVERYTHING).reset_index(drop=True)
plays["y"] = plays["label"].map({c: i for i, c in enumerate(CLASSES)})

train = plays[plays["season"] < TEST_SEASON]
test = plays[plays["season"] == TEST_SEASON].reset_index(drop=True)
print(f"Training plays: {len(train):,} (2018-2024)   Test plays: {len(test):,} ({TEST_SEASON})\n")


# ---------- Baselines (no "learning", just counting) ----------

def baseline_most_common():
    """Trial 1: always guess the most common answer. Its 'probabilities' are just how often each answer happened in training."""
    freq = train["y"].value_counts(normalize=True).reindex(range(len(CLASSES)), fill_value=0).to_numpy()
    return np.tile(freq, (len(test), 1))


def baseline_ball_team():
    """Baseline 2: only knows WHICH team has the ball (home team or away team)."""
    probs = np.zeros((len(test), len(CLASSES)))
    for home in (0, 1):
        freq = (train.loc[train["is_home"] == home, "y"].value_counts(normalize=True)
                .reindex(range(len(CLASSES)), fill_value=0).to_numpy())
        probs[test["is_home"].to_numpy() == home] = freq
    return probs


# ---------- Real models ----------

def logistic(features):
    """Multinomial logistic regression: a simple 'weighted points' model. Each input gets a weight for each answer."""
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
    model.fit(train[features], train["y"])
    return model.predict_proba(test[features]), model


def boosted_trees(features):
    """XGBoost: builds hundreds of small decision trees, each one fixing the mistakes of the ones before it."""
    params = dict(objective="multi:softprob", num_class=len(CLASSES), max_depth=4,
                  learning_rate=0.08, subsample=0.8, colsample_bytree=0.9,
                  min_child_weight=20, eval_metric="mlogloss", tree_method="hist", seed=42)
    # Use 2024 as a "practice test" to decide how many trees to build (so we never peek at 2025).
    fit_part, check_part = train[train["season"] < 2024], train[train["season"] == 2024]
    trial = xgb.train(params, xgb.DMatrix(fit_part[features], fit_part["y"]), num_boost_round=1000,
                      evals=[(xgb.DMatrix(check_part[features], check_part["y"]), "check")],
                      early_stopping_rounds=30, verbose_eval=False)
    n_trees = trial.best_iteration + 1
    model = xgb.train(params, xgb.DMatrix(train[features], train["y"]), num_boost_round=n_trees)
    print(f"   (XGBoost chose {n_trees} rounds of trees)")
    return model.predict(xgb.DMatrix(test[features])), model


# ---------- Scoring ----------

def calibration_error(probs, y, bins=10):
    """When the model's #1 pick got (say) 40%, was it right about 40% of the time? This is the average gap."""
    p = probs.max(1)
    hit = probs.argmax(1) == y
    which_bin = np.minimum((p * bins).astype(int), bins - 1)
    gap = 0.0
    for b in range(bins):
        in_bin = which_bin == b
        if in_bin.any():
            gap += in_bin.mean() * abs(p[in_bin].mean() - hit[in_bin].mean())
    return gap


def who_only(idx):
    """Collapse an answer to just WHO scores: 0 = ball team, 1 = other team, 2 = nobody."""
    return np.where(idx < 5, 0, np.where(idx < 10, 1, 2))


def bootstrap_ci(probs, y, games, n=500, seed=0):
    """Re-run the test on 500 random 'remixes' of the 2025 games to see how much the scores could wobble by luck."""
    rng = np.random.default_rng(seed)
    per_play_loss = -np.log(np.clip(probs[np.arange(len(y)), y], 1e-15, 1))
    per_play_hit = probs.argmax(1) == y
    frame = pd.DataFrame({"g": games, "loss": per_play_loss, "hit": per_play_hit, "n": 1}).groupby("g").sum()
    accs, losses = [], []
    for _ in range(n):
        s = frame.iloc[rng.integers(0, len(frame), len(frame))].sum()
        accs.append(s["hit"] / s["n"])
        losses.append(s["loss"] / s["n"])
    return np.percentile(accs, [2.5, 97.5]), np.percentile(losses, [2.5, 97.5]), frame


y_test = test["y"].to_numpy()
# (short key, name for the table, inputs used, how to run it)
trials = [
    ("t1", "1. Baseline: always guess most common", "none", baseline_most_common),
    ("b2", "Baseline 2: only which team has ball", "home/away", baseline_ball_team),
    ("t2", "2. Field position only", "yard line", lambda: logistic(FIELD)),
    ("t3", "3. Field position + down + distance", "yard line, down, distance", lambda: logistic(FIELD_DOWN)),
    ("t4", "4. Everything (logistic regression)", "all 10 inputs", lambda: logistic(EVERYTHING)),
    ("t5", "5. Everything (XGBoost)", "all 10 inputs", lambda: boosted_trees(EVERYTHING)),
    # Bonus fairness check: same stronger model type, but fewer inputs.
    ("x2", "Bonus: XGBoost, field position only", "yard line", lambda: boosted_trees(FIELD)),
    ("x3", "Bonus: XGBoost, field position + down + distance", "yard line, down, distance", lambda: boosted_trees(FIELD_DOWN)),
]

rows, all_probs = [], {}
for key, name, inputs, run in trials:
    print(f"Running: {name}")
    out = run()
    probs = out[0] if isinstance(out, tuple) else out
    model = out[1] if isinstance(out, tuple) else None
    all_probs[key] = probs
    acc_ci, loss_ci, _ = bootstrap_ci(probs, y_test, test["game_id"].to_numpy())
    rows.append({
        "trial": name,
        "inputs": inputs,
        "accuracy_%": 100 * accuracy_score(y_test, probs.argmax(1)),
        "accuracy_95%_range": f"{100*acc_ci[0]:.1f}-{100*acc_ci[1]:.1f}",
        "who_scores_accuracy_%": 100 * (who_only(probs.argmax(1)) == who_only(y_test)).mean(),
        "log_loss": log_loss(y_test, probs, labels=range(len(CLASSES))),
        "log_loss_95%_range": f"{loss_ci[0]:.3f}-{loss_ci[1]:.3f}",
        "calibration_error_%": 100 * calibration_error(probs, y_test),
    })
    if key == "t5":
        model.save_model("results/xgb_model.json")

results = pd.DataFrame(rows)
results.to_csv("results/trial_results.csv", index=False, float_format="%.4f")

# Is trial 5 REALLY better than trial 4, or could it be luck? Compare them on the same random game remixes.
loss4 = -np.log(np.clip(all_probs["t4"][np.arange(len(y_test)), y_test], 1e-15, 1))
loss5 = -np.log(np.clip(all_probs["t5"][np.arange(len(y_test)), y_test], 1e-15, 1))
diff = pd.DataFrame({"g": test["game_id"], "d": loss4 - loss5, "n": 1}).groupby("g").sum()
rng = np.random.default_rng(1)
boot = [s["d"] / s["n"] for s in (diff.iloc[rng.integers(0, len(diff), len(diff))].sum() for _ in range(500))]
share_better = float(np.mean(np.array(boot) > 0))

# Save test predictions + useful info for the graphs step.
pred = test[EVERYTHING + ["game_id", "label", "y"]].copy()
for key, probs in all_probs.items():
    np.save(f"results/probs_{key}.npy", probs)
pred.to_parquet("results/test_plays.parquet")
json.dump({"classes": CLASSES, "features": EVERYTHING, "trials": {t[0]: t[1] for t in trials},
           "test_games": int(test["game_id"].nunique()), "train_plays": len(train), "test_plays": len(test),
           "xgb_beats_logistic_in_%_of_remixes": 100 * share_better,
           "most_common_answer": CLASSES[int(train["y"].mode()[0])]},
          open("results/info.json", "w"), indent=2)

pd.set_option("display.width", 200)
print("\nRESULTS (tested on the 2025 season):")
print(results.drop(columns=["inputs"]).round(3).to_string(index=False))
print(f"\nXGBoost had lower log loss than logistic regression in {100*share_better:.0f}% of 500 random remixes of the 2025 games.")

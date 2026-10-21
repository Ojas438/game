"""
STEP 4: MAKE THE GRAPHS FOR THE DISPLAY BOARD

Makes these PNG pictures in the graphs/ folder:
  1_trial_comparison.png     - accuracy and log loss for every trial
  2_fairness_check.png       - is it the INPUTS or the MODEL TYPE that helps?
  3_feature_importance.png   - which game factors matter most (grouped)
  3b_feature_importance_detail.png - same idea, every single input
  4_calibration.png          - when the model says 30%, does it happen ~30% of the time?
  5_down_the_field.png       - how the predictions change as a team drives down the field

Run it with:   python 04_make_graphs.py
"""

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import log_loss

# Colors (a color-blind-safe palette) and chart style
BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"
GRAY, INK, INK2, GRID, SURFACE = "#b5b3ab", "#0b0b0b", "#52514e", "#e1e0d9", "#fcfcfb"
plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "font.size": 13, "axes.titlesize": 17, "axes.titleweight": "bold", "axes.labelsize": 13,
    "axes.edgecolor": "#c3c2b7", "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "text.color": INK, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
})

info = json.load(open("results/info.json"))
CLASSES, FEATURES = info["classes"], info["features"]
results = pd.read_csv("results/trial_results.csv")
test = pd.read_parquet("results/test_plays.parquet")
y = test["y"].to_numpy()
probs = {k: np.load(f"results/probs_{k}.npy") for k in info["trials"]}
model = xgb.Booster()
model.load_model("results/xgb_model.json")


def ci_bars(col, scale=1.0):
    lo_hi = results[col].str.split("-", expand=True).astype(float) * scale
    return lo_hi[0].to_numpy(), lo_hi[1].to_numpy()


def save(fig, name):
    fig.tight_layout()
    fig.savefig(f"graphs/{name}", dpi=170)
    plt.close(fig)
    print(f"saved graphs/{name}")


# ---------- 1. Trial comparison ----------
main = results.iloc[:6].reset_index(drop=True)
short = ["1. Always guess\nmost common", "Baseline 2:\nwhich team\nhas ball", "2. Field\nposition only",
         "3. + down &\ndistance", "4. Everything\n(logistic)", "5. Everything\n(XGBoost)"]
colors = [GRAY, GRAY, BLUE, BLUE, BLUE, ORANGE]
fig, axes = plt.subplots(1, 2, figsize=(16, 6.8))
for ax, col, ci_col, title, better in [
    (axes[0], "accuracy_%", "accuracy_95%_range", "Accuracy (higher is better)", "% of plays where the top guess was exactly right"),
    (axes[1], "log_loss", "log_loss_95%_range", "Log loss (lower is better)", "How 'surprised' the model was on average"),
]:
    lo, hi = ci_bars(ci_col)
    lo, hi = lo[:6], hi[:6]
    vals = main[col].to_numpy()
    ax.bar(short, vals, color=colors, width=0.62, edgecolor=SURFACE, linewidth=2,
           yerr=[vals - lo, hi - vals], ecolor=INK2, capsize=5)
    for i, v in enumerate(vals):
        ax.text(i, hi[i] + (0.6 if col == "accuracy_%" else 0.02), f"{v:.1f}%" if col == "accuracy_%" else f"{v:.3f}",
                ha="center", va="bottom", fontsize=12, fontweight="bold", color=INK)
    ax.set_title(title)
    ax.set_ylabel(better)
    ax.grid(axis="x", visible=False)
    if col == "log_loss":
        ax.set_ylim(1.4, 2.0)
    else:
        ax.set_ylim(0, 45)
    ax.tick_params(axis="x", labelsize=11)
fig.suptitle("Which trial predicted the next score best? (tested on all 2025 NFL plays)", fontsize=19, fontweight="bold")
fig.text(0.5, 0.005, "Gray = baselines (simple guessing)   Blue = logistic regression   Orange = XGBoost.   "
         "Black lines show the 95% range if the 2025 games were randomly re-drawn.", ha="center", fontsize=11, color=INK2)
fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.savefig("graphs/1_trial_comparison.png", dpi=170)
plt.close(fig)
print("saved graphs/1_trial_comparison.png")


# ---------- 2. Fairness check: inputs vs model type ----------
fig, ax = plt.subplots(figsize=(11, 6.5))
groups = ["Field position\nonly", "Field position\n+ down & distance", "Everything"]
logit = results.set_index("trial").loc[[info["trials"][k] for k in ("t2", "t3", "t4")], "log_loss"].to_numpy()
boost = results.set_index("trial").loc[[info["trials"][k] for k in ("x2", "x3", "t5")], "log_loss"].to_numpy()
x = np.arange(3)
ax.bar(x - 0.18, logit, 0.34, color=BLUE, label="Logistic regression", edgecolor=SURFACE, linewidth=2)
ax.bar(x + 0.18, boost, 0.34, color=ORANGE, label="XGBoost", edgecolor=SURFACE, linewidth=2)
for xi, v in zip(list(x - 0.18) + list(x + 0.18), list(logit) + list(boost)):
    ax.text(xi, v + 0.008, f"{v:.3f}", ha="center", fontsize=12, fontweight="bold")
base = results.loc[0, "log_loss"]
ax.axhline(base, color=INK2, linestyle="--", linewidth=1.5)
ax.text(2.45, base + 0.008, f"Always-guess baseline ({base:.3f})", ha="right", color=INK2, fontsize=11)
ax.set_xticks(x, groups)
ax.set_ylim(1.4, 1.95)
ax.set_ylabel("Log loss (lower is better)")
ax.set_title("Fairness check: more INPUTS helps much more than a fancier MODEL")
ax.grid(axis="x", visible=False)
ax.legend(frameon=False, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 0.93))
save(fig, "2_fairness_check.png")


# ---------- 3. Feature importance (permutation importance) ----------
# Idea: scramble one input across all 2025 plays (so it becomes useless noise) and
# see how much worse the model gets. Bigger damage = more important input.
X = test[FEATURES].copy()
start_loss = log_loss(y, probs["t5"], labels=range(len(CLASSES)))
rng = np.random.default_rng(7)


def damage(columns, repeats=3):
    hurt = []
    for _ in range(repeats):
        Xs = X.copy()
        order = rng.permutation(len(Xs))
        for c in columns:  # shuffle grouped columns together so they stay consistent with each other
            Xs[c] = Xs[c].to_numpy()[order]
        hurt.append(log_loss(y, model.predict(xgb.DMatrix(Xs)), labels=range(len(CLASSES))) - start_loss)
    return float(np.mean(hurt))


GROUPS = {
    "Clock (time left + quarter)": ["half_seconds_remaining", "game_seconds_remaining", "qtr"],
    "Field position (yard line)": ["yardline_100"],
    "Score (who's winning, by how much)": ["score_differential"],
    "Down & distance": ["down", "ydstogo"],
    "Timeouts left": ["posteam_timeouts_remaining", "defteam_timeouts_remaining"],
    "Home or away": ["is_home"],
}
NICE = {"yardline_100": "Yard line", "down": "Down", "ydstogo": "Yards to go", "score_differential": "Score difference",
        "half_seconds_remaining": "Seconds left in half", "game_seconds_remaining": "Seconds left in game",
        "qtr": "Quarter", "posteam_timeouts_remaining": "Offense timeouts", "defteam_timeouts_remaining": "Defense timeouts",
        "is_home": "Home team has ball"}

grouped = pd.Series({g: damage(cols) for g, cols in GROUPS.items()}).sort_values()
single = pd.Series({NICE[f]: damage([f]) for f in FEATURES}).sort_values()
pd.DataFrame({"importance": pd.concat([grouped, single])}).to_csv("results/feature_importance.csv")

for data, name, title in [(grouped, "3_feature_importance.png", "Which game factors matter most?"),
                          (single, "3b_feature_importance_detail.png", "Importance of every single input")]:
    fig, ax = plt.subplots(figsize=(11, 0.75 * len(data) + 2))
    ax.barh(data.index, data.values, color=BLUE, height=0.6)
    for i, v in enumerate(data.values):
        ax.text(v + data.max() * 0.01, i, f"+{v:.3f}", va="center", fontsize=12, fontweight="bold")
    ax.set_xlabel("How much worse log loss gets when this factor is scrambled (bigger = more important)")
    ax.set_title(title)
    ax.set_xlim(0, data.max() * 1.15)
    ax.grid(axis="y", visible=False)
    save(fig, name)


# ---------- 4. Calibration ----------
def reliability(p, hit, edges):
    centers, actual, counts = [], [], []
    for a, b in zip(edges[:-1], edges[1:]):
        m = (p >= a) & (p < b)
        if m.sum() >= 50:  # skip bins with too few plays to trust
            centers.append(p[m].mean())
            actual.append(hit[m].mean())
            counts.append(m.sum())
    return np.array(centers), np.array(actual), np.array(counts)


fig, axes = plt.subplots(1, 2, figsize=(16, 7.6))
pct = matplotlib.ticker.PercentFormatter(1.0, decimals=0)
edges = np.linspace(0, 1, 21)

# Left: every predicted chance for every answer, for the two "everything" models.
ax = axes[0]
ax.plot([0, 1], [0, 1], color=INK2, linestyle="--", linewidth=1.5, label="Perfect calibration")
for key, label, color in [("t4", "4. Everything (logistic)", BLUE), ("t5", "5. Everything (XGBoost)", ORANGE)]:
    P = probs[key]
    hit = (np.arange(len(CLASSES))[None, :] == y[:, None]).ravel()
    cx, ay, _ = reliability(P.ravel(), hit, edges)
    ax.plot(cx, ay, color=color, linewidth=2.5, marker="o", markersize=8, markeredgecolor=SURFACE,
            markeredgewidth=2, label=label)
ax.set_title("Both models, every answer")

# Right: the XGBoost model, one line per common answer.
ax = axes[1]
ax.plot([0, 1], [0, 1], color=INK2, linestyle="--", linewidth=1.5, label="Perfect calibration")
for name, color in [("Ball team: Field Goal", AQUA), ("Ball team: Passing TD", BLUE), ("No Score", YELLOW)]:
    k = CLASSES.index(name)
    cx, ay, _ = reliability(probs["t5"][:, k], y == k, edges)
    ax.plot(cx, ay, color=color, linewidth=2.5, marker="o", markersize=8, markeredgecolor=SURFACE,
            markeredgewidth=2, label=name)
ax.set_title("XGBoost, one line per common answer")

for ax in axes:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.set_xlabel("What the model said (predicted chance)")
    ax.set_ylabel("What really happened (actual rate)")
    ax.xaxis.set_major_formatter(pct)
    ax.yaxis.set_major_formatter(pct)
    ax.legend(frameon=False, loc="upper left", fontsize=11)
fig.suptitle("Calibration: when the model says 30%, does it happen about 30% of the time?\n"
             "Points close to the dashed line = honest probabilities  (2025 test season)", fontsize=17, fontweight="bold")
save(fig, "4_calibration.png")


# ---------- 5. Down the field ----------
# A made-up but typical situation: 1st & 10, 1st quarter with 12:00 left, tie game, 3 timeouts each, home team has ball.
yard = np.arange(99, 0, -1)
scenario = pd.DataFrame({
    "yardline_100": yard, "down": 1, "ydstogo": np.minimum(10, yard), "score_differential": 0,
    "half_seconds_remaining": 1620, "game_seconds_remaining": 3420, "qtr": 1,
    "posteam_timeouts_remaining": 3, "defteam_timeouts_remaining": 3, "is_home": 1,
})[FEATURES]
P = model.predict(xgb.DMatrix(scenario))
col = {c: i for i, c in enumerate(CLASSES)}
bands = [
    ("Ball team: Passing TD", P[:, col["Ball team: Passing TD"]], BLUE),
    ("Ball team: Rushing TD", P[:, col["Ball team: Rushing TD"]], ORANGE),
    ("Ball team: Field Goal", P[:, col["Ball team: Field Goal"]], AQUA),
    ("No Score", P[:, col["No Score"]], YELLOW),
    ("Other team: any TD or FG", sum(P[:, col[f"Other team: {h}"]] for h in ["Passing TD", "Rushing TD", "Field Goal"]), MAGENTA),
    ("Rare: any safety or return TD", sum(P[:, col[c]] for c in CLASSES if "Safety" in c or "Return" in c), GREEN),
]
fig, ax = plt.subplots(figsize=(15, 7.5))
x = 100 - yard  # 1 = own 1-yard line ... 99 = opponent's 1-yard line
ax.stackplot(x, [b[1] for b in bands], labels=[b[0] for b in bands], colors=[b[2] for b in bands],
             edgecolor=SURFACE, linewidth=1.5, alpha=0.95)
ax.set_xlim(1, 99)
ax.set_ylim(0, 1)
ax.set_xticks([1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 99],
              ["Own 1", "Own 10", "Own 20", "Own 30", "Own 40", "50", "Opp 40", "Opp 30", "Opp 20", "Opp 10", "Opp 1"])
ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
ax.set_ylabel("Chance of being the next score")
ax.set_xlabel("Where the team with the ball is on the field  →  driving toward the opponent's end zone")
ax.set_title("As a team drives down the field, its chance to score next goes way up\n"
             "(1st & 10, tie game, 12:00 left in the 1st quarter, XGBoost model)")
ax.grid(False)
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles[::-1], labels[::-1], frameon=True, facecolor=SURFACE, edgecolor=GRID, loc="center left",
          bbox_to_anchor=(1.01, 0.5), fontsize=12)
for spot in (20, 50, 80):
    i = list(x).index(spot)
    ball = P[i, :5].sum()
    ax.annotate(f"Ball team scores next: {ball:.0%}", (spot, 0.03), ha="center", fontsize=11, fontweight="bold",
                color=INK, bbox=dict(boxstyle="round,pad=0.3", fc=SURFACE, ec=GRID))
save(fig, "5_down_the_field.png")
pd.DataFrame(P, columns=CLASSES, index=pd.Index(x, name="field_position_1_to_99")).round(4).to_csv(
    "results/down_the_field.csv")

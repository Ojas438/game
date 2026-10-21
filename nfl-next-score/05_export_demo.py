"""
STEP 5: EXPORT THE BEST MODEL FOR THE WEB DEMO

What this does, in plain English:
  The XGBoost model is just a big pile of small yes/no decision trees.
  We copy every tree into a small file (demo/model.json) so the web page can walk
  through the trees itself, right in the visitor's browser. No server needed!

  We also save a few test situations with the answers Python gave, so we can check
  the web page gets exactly the same numbers (results/check_cases.json).

Run it with:   python 05_export_demo.py
"""

import json

import numpy as np
import pandas as pd
import xgboost as xgb

info = json.load(open("results/info.json"))
raw = json.load(open("results/xgb_model.json"))["learner"]
booster = raw["gradient_booster"]["model"]

trees = []
for tree, which_class in zip(booster["trees"], booster["tree_info"]):
    left, right = tree["left_children"], tree["right_children"]
    trees.append({
        "c": which_class,                 # which of the 11 answers this tree votes for
        "l": left, "r": right,            # where to go next (-1 means "this is a leaf")
        "f": tree["split_indices"],       # which input this node asks about
        # For a question node: the cut-off number. For a leaf: the tree's vote.
        "v": [float(np.float32(v)) for v in tree["split_conditions"]],
    })

model = {
    "classes": info["classes"],
    "features": info["features"],
    "base": [float(v) for v in raw["learner_model_param"]["base_score"].strip("[]").split(",")],
    "trees": trees,
}
json.dump(model, open("demo/model.json", "w"), separators=(",", ":"))

# Pick 300 random 2025 plays and record what Python's XGBoost predicts for them.
test = pd.read_parquet("results/test_plays.parquet").sample(300, random_state=0)
real = xgb.Booster()
real.load_model("results/xgb_model.json")
cases = {"inputs": test[info["features"]].to_numpy().tolist(),
         "python_probs": real.predict(xgb.DMatrix(test[info["features"]])).tolist()}
json.dump(cases, open("results/check_cases.json", "w"))
print(f"Exported {len(trees)} trees to demo/model.json")

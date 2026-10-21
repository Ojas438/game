"""
STEP 1: GET THE DATA

What this does, in plain English:
  The nflverse project records every single play of every NFL game for free.
  This script downloads every play from the 2018 through 2025 seasons and
  saves only the columns (pieces of information) we need into one file.

Run it with:   python 01_get_data.py
"""

import nflreadpy as nfl

SEASONS = list(range(2018, 2026))  # 2018, 2019, ... 2025

# The columns we keep. Each one is a fact about a play.
COLUMNS = [
    "game_id", "play_id", "season", "season_type",
    "home_team", "posteam", "defteam",           # who is home, who has the ball, who is defending
    "game_half", "qtr", "down", "ydstogo",       # which half/quarter, which down, yards needed for a 1st down
    "yardline_100",                              # yards away from the end zone (1 = almost scoring, 99 = backed up)
    "half_seconds_remaining", "game_seconds_remaining",
    "score_differential",                        # (score of team with ball) minus (score of other team)
    "posteam_timeouts_remaining", "defteam_timeouts_remaining",
    "play_type", "desc",
    # These columns tell us if/how a play scored:
    "touchdown", "td_team", "pass_touchdown", "rush_touchdown", "return_touchdown",
    "field_goal_result", "safety",
]

print(f"Downloading seasons {SEASONS[0]}-{SEASONS[-1]} (this can take a minute)...")
plays = nfl.load_pbp(SEASONS).select(COLUMNS).to_pandas()
plays.to_parquet("data/plays_raw.parquet")

print(f"Saved {len(plays):,} plays from {plays['game_id'].nunique():,} games to data/plays_raw.parquet")
print(plays.groupby("season").size().rename("plays per season").to_string())

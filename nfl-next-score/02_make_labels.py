"""
STEP 2: LABEL EVERY PLAY WITH "WHAT WAS THE NEXT SCORE?"

What this does, in plain English:
  For each play, we look forward in time (inside the same half of the same game)
  until we find the next score. That score is the "answer" for the play.

  The answer is written from the point of view of the team that has the ball:
     "Ball team"  = the team on offense right now
     "Other team" = the team on defense right now
  ...plus HOW they scored: Passing TD, Rushing TD, Field Goal, Safety, or Return TD.
  If nobody scores before the half ends, the answer is "No Score".

  That gives 11 possible answers ("classes"):
     5 ways for the ball team + 5 ways for the other team + "No Score".

Run it with:   python 02_make_labels.py
"""

import pandas as pd

HOW = ["Passing TD", "Rushing TD", "Field Goal", "Safety", "Return TD"]
CLASSES = [f"Ball team: {h}" for h in HOW] + [f"Other team: {h}" for h in HOW] + ["No Score"]

plays = pd.read_parquet("data/plays_raw.parquet")

# Overtime has different rules, so we leave it out and only use the two regular halves.
plays = plays[plays["game_half"].isin(["Half1", "Half2"])].copy()
plays = plays.sort_values(["game_id", "play_id"]).reset_index(drop=True)


def score_on_this_play(play):
    """If this play scored points, return (team that scored, how). Otherwise return None."""
    if play["touchdown"] == 1 and pd.notna(play["td_team"]):
        if play["pass_touchdown"] == 1:
            how = "Passing TD"
        elif play["rush_touchdown"] == 1:
            how = "Rushing TD"
        else:
            how = "Return TD"  # kick/punt returns, interceptions, fumble recoveries, blocked kicks
        return play["td_team"], how
    if play["field_goal_result"] == "made":
        return play["posteam"], "Field Goal"
    if play["safety"] == 1:
        return play["defteam"], "Safety"  # the defending team gets the 2 points
    return None


# Walk BACKWARDS through each half. Going backwards makes it easy:
# we always remember "the most recent score we've seen", which is the NEXT score for earlier plays.
next_team, next_how = [None] * len(plays), [None] * len(plays)
for (game, half), idx in plays.groupby(["game_id", "game_half"]).groups.items():
    upcoming = (None, "No Score")
    for i in sorted(idx, reverse=True):
        scored = score_on_this_play(plays.loc[i])
        if scored is not None:
            upcoming = scored
        next_team[i], next_how[i] = upcoming

plays["next_score_team"] = next_team
plays["next_score_how"] = next_how

# Keep only normal plays from scrimmage (1st-4th down) where a team has the ball.
# (Kickoffs and extra points don't have a down, so they are left out.)
plays = plays[plays["down"].notna() & plays["posteam"].notna()].copy()


def make_label(row):
    if row["next_score_how"] == "No Score":
        return "No Score"
    side = "Ball team" if row["next_score_team"] == row["posteam"] else "Other team"
    return f"{side}: {row['next_score_how']}"


plays["label"] = plays.apply(make_label, axis=1)
plays["is_home"] = (plays["posteam"] == plays["home_team"]).astype(int)

plays.to_parquet("data/plays_labeled.parquet")

print(f"Labeled {len(plays):,} plays.\n")
print("How often each answer happens (all seasons):")
pct = plays["label"].value_counts(normalize=True).reindex(CLASSES).fillna(0) * 100
print(pct.round(2).astype(str).add(" %").to_string())

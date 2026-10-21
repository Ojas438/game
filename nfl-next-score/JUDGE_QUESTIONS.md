# 10 Questions Judges Might Ask (with answers)

Practice saying these in your own words. You don't need to memorize them exactly.

---

**1. In one sentence, what does your project do?**
> It uses the game situation (yard line, down, score, clock, and more) to predict the chance of each possible next score in an NFL game. I tested whether more information and a stronger model predict better than simple guessing.

**2. Where did your data come from, and how much did you use?**
> From nflverse, a free public project that records every NFL play. I used 8 seasons (2018–2025). After cleaning, I had about 325,000 plays: 284,000 for training and 40,500 from the 2025 season for testing.

**3. Why did you test on a different season than you trained on?**
> To make the test fair. If I tested on plays the model already studied, it would be like taking a test after seeing the answer key. Testing on 2025, which it never saw, shows whether it learned real patterns that work on new games.

**4. How did you figure out the "right answer" for each play?**
> For every play, my program looks forward in the same half until it finds the next score. That score is the answer. If the half ends with no score, the answer is "No Score." I wrote the answer from the point of view of the team with the ball, so "Ball team: Field Goal" means the offense kicked the next field goal.

**5. What is log loss, and why did you use it instead of just accuracy?**
> Log loss is a "surprise score." The model gets a small penalty when something it expected happens and a big penalty when something it said was very unlikely happens. Lower is better. Accuracy only checks the #1 guess, so it ignores whether the model's percentages were honest. For example, my field-position-only model had almost the same accuracy as guessing, but a better log loss, because its percentages got more realistic even when its top guess didn't change.

**6. What does "calibration" mean?**
> It means the percentages are honest. If the model says "30%" for a lot of plays, that thing should happen in about 30% of those plays. My calibration chart shows the best model's points sit right next to the "perfect" line, and its average gap was only about 1.2 percentage points.

**7. Was your hypothesis correct?**
> Partly. My hypothesis that more information would make better predictions was supported: every time I added information, log loss went down. My hypothesis that field position would matter most was not supported. Field position came second; the clock was first. That surprised me, but it makes sense: when time is almost out, usually nobody scores, and the clock decides how many chances each team has left.

**8. How do you know your results weren't just luck?**
> I re-drew the 285 test games randomly 500 times and re-scored each model each time. That gives a "95% range" for each result. The best model's range doesn't overlap with the guessing baseline at all, and XGBoost beat the simpler model in all 500 re-draws. I re-drew whole games instead of single plays, because plays from the same drive are connected.

**9. Why is the best model only right 38% of the time? Isn't that bad?**
> There are 11 possible answers, and football has a lot of luck, like fumbles, interceptions, and missed kicks. Even the most common answer only happens about 26% of the time. So 38% is a big improvement over 28% from guessing. Also, the model's percentages are honest, which is more useful than a single guess. For *who* scores next (ball team, other team, or nobody), it was right 69% of the time.

**10. If you kept working on this, what would you change?**
> I'd add team strength, because the model doesn't know if it's a great team or a bad team, and I think that's the biggest missing piece. I'd also try adding weather and the quarterback, and test it live during real games.

---

### Bonus quick answers

- **What is XGBoost?** A model that builds hundreds of small yes/no decision trees. Each new tree tries to fix the mistakes of the trees before it, and all their votes are added together.
- **What is logistic regression?** A simpler model that gives each input a "weight" for each outcome, adds them up, and turns the totals into percentages.
- **What is a "feature"?** One piece of information the model uses, like the yard line or the score.
- **What did the fairness check show?** Giving XGBoost only field position barely helped. Most of the improvement came from adding more information, not from the fancier model.
- **Why didn't "which team has the ball" help (Baseline 2)?** I measured that as home team vs away team. Home teams score next only slightly more often, so it barely changed anything (log loss 1.8969 vs 1.8974).

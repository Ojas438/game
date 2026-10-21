# Results and Conclusion (for the display board)

*All numbers come from testing on the 2025 NFL season (40,516 plays, 285 games). The models never saw these plays during training.*

## Hypotheses

Write down whichever hypothesis you actually believed **before** you saw the results. Science fair judges care about honesty, and a hypothesis that turns out wrong is still good science.

- **Hypothesis A:** "If the model is given more information about the game situation, then it will predict the next score better than a model that only knows field position, because the score and the clock change what teams try to do."
- **Hypothesis B:** "Field position (the yard line) will be the most important factor for predicting the next score."

## Results

1. **Every real model beat simple guessing on log loss.** Guessing the most common outcome every time ("Ball team: Field Goal") was right 28.1% of the time, with a log loss of 1.897.
2. **Adding more information helped a lot.** Log loss went from 1.827 (field position only) to 1.805 (adding down & distance) to 1.654 (adding score, time, quarter, timeouts, and home/away).
3. **Accuracy only jumped once the clock and score were added.** It went from about 28% to 35.5%. With only field position, the model's #1 guess was usually still "Field Goal," so its top guess rarely changed. Its percentages did get more honest, which is why log loss improved even though accuracy didn't.
4. **The stronger model type (XGBoost) did best:** 38.2% accuracy, log loss 1.579, and the smallest calibration error (1.2%). It beat the simpler model in 100% of 500 random re-draws of the 2025 games, so this was not luck.
5. **More information mattered more than a fancier model.** XGBoost with only field position (1.815) was barely better than the simple model with field position (1.827). With all the information, the simple model improved to 1.654 and XGBoost to 1.579.
6. **The predicted percentages are honest (well calibrated).** When the best model said something had a 20%, 40%, or 60% chance, it happened about 20%, 40%, or 60% of the time.
7. **Most important factors:** clock (time left + quarter) > field position > score > down & distance > timeouts > home/away. Scrambling the clock hurt the model about twice as much as scrambling the yard line.
8. **Who is easier to predict than how.** The best model picked the correct *team* (or "nobody") 69% of the time, but the exact *team + way of scoring* only 38% of the time.
9. **Driving down the field:** with 1st & 10 in a tie game early in the 1st quarter, the chance that the team with the ball scores next goes from 57% at its own 20, to 76% at midfield, to 95% at the opponent's 20.

## Conclusion

**Yes, a computer model can predict who will score next and how, better than simple guessing.** The best model (XGBoost with all 10 inputs) was right 38% of the time compared with 28% for guessing. Its log loss was about 17% lower, and its percentages matched reality closely.

- **Hypothesis A was supported.** Each time more game information was added, predictions got better. The biggest jump came from adding the score and the clock.
- **Hypothesis B was not supported.** Field position was very important (#2), but the **clock was #1**. This makes sense: with only a little time left in a half, often *nobody* scores, and the team with the ball is the only one with a real chance. Time decides how many chances each team still has to score.

## Limitations

- The model doesn't know which teams or players are playing.
- Plays from the same drive share an answer, so they aren't fully independent tests. I handled this by re-drawing whole games when calculating my 95% ranges.
- Rare outcomes (safeties, return TDs) are hard to predict because there are few examples.
- Overtime was left out.
- Football has a lot of luck (fumbles, tipped passes), so even a perfect model couldn't be right every time.

## Future work

- Add team strength (point spreads, records), weather, and the quarterback.
- Test on more seasons to see whether the patterns change over time.
- Try other model types (like neural networks) and compare.
- Use the model live during a real game.

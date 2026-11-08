# Sources for the paper

Each source has its full reference, a link, what it found, and how it
connects to this project. Read at least each abstract yourself before citing
it. These summaries come from search results, not from reading every paper in
full.

## Closest to this project

**Wolfson, J., & Koopmeiners, J. S. Who's good this year? Comparing the
information content of games in the four major US sports. *Journal of Sports
Analytics*. (First posted on arXiv in 2015.)**
<https://arxiv.org/abs/1501.07179>

Check the journal's volume, issue and year on the journal's page before
citing it. I couldn't confirm them.

- Tested how prediction accuracy changes as more games are added to the
  training data, in the NFL, NBA, NHL and MLB.
- In the NFL, accuracy kept improving as more games were added within a
  season. In the NBA it stopped improving early, at about 25 to 30 games.
- Connection: the same question as this project (does more data keep
  helping?), but within one season. This project looks across many seasons
  and finds a point where more data stops helping.

**Lopez, M. J., Matthews, G. J., & Baumer, B. S. (2018). How often does the
best team win? A unified approach to understanding randomness in North
American sport. *Annals of Applied Statistics*, 12(4), 2483–2516.**
<https://arxiv.org/abs/1701.05976>

- Measured how much luck decides games in each league. NFL and NBA games
  are less random than NHL and MLB games.
- Points out that teams play each other only about once a season, so game
  results alone can't pin down exactly how good a team is.
- Connection: explains why no predictor can get close to 100%, and why the
  betting market (which uses more information) does better than this
  project's predictors.

## How the algorithm works (team ratings)

**Massey, K. (1997). *Statistical models applied to the rating of sports
teams* [Honors project, Bluefield College].**
<https://masseyratings.com/theory/massey97.pdf>

- Rates teams so that the difference between two teams' ratings predicts the
  score margin, using least squares.
- Connection: this project's team ratings use the same idea, with a home-field
  bonus and four extra pieces of information added.

**Stern, H. (1991). On the probability of winning a football game. *The
American Statistician*, 45(3), 179–183.
<https://doi.org/10.1080/00031305.1991.10475798>**

- Showed that NFL score margins are roughly spread around the betting point
  spread, give or take about 14 points.
- Connection: shows why a predicted margin of a few points still leaves a lot
  of uncertainty about who wins.

## How much data AI needs

**Hoffmann, J., et al. (2022). Training compute-optimal large language
models. arXiv:2203.15556.**
<https://arxiv.org/abs/2203.15556>

- Showed that for a fixed amount of computing, there is a best balance
  between model size and the amount of training data. Many large AI models
  were not trained in the most efficient way.
- Connection: the large-scale version of this project's question: how to get
  the best result for the computing (and water) spent.

**Sorscher, B., Geirhos, R., Shekhar, S., Ganguli, S., & Morcos, A. S.
(2022). Beyond neural scaling laws: Beating power law scaling via data
pruning. *NeurIPS 2022* (Outstanding Paper Award).**
<https://arxiv.org/abs/2206.14486>

- Showed that choosing which training examples to keep, and throwing out
  the rest, can get the same accuracy from much less data.
- Connection: this project found the same kind of thing. The most recent few
  hundred games did as well as using every game since 1999.

## Why old data can hurt (concept drift)

**Gama, J., Žliobaitė, I., Bifet, A., Pechenizkiy, M., & Bouchachia, A.
(2014). A survey on concept drift adaptation. *ACM Computing Surveys*,
46(4), Article 44.**
<https://doi.org/10.1145/2523813>

- "Concept drift" means the patterns in data change over time, so a model
  trained on old data gets worse. The survey explains how to detect and
  handle it.
- Connection: explains why the first version of the predictors got worse
  with games from 10 or 20 years ago. Teams change, so old games teach the
  wrong lessons.

## AI and water

**Li, P., Yang, J., Islam, M. A., & Ren, S. (2023). Making AI less "thirsty":
Uncovering and addressing the secret water footprint of AI models.
arXiv:2304.03271. Accepted by *Communications of the ACM*.**
<https://arxiv.org/abs/2304.03271>

- Estimated that training GPT-3 in Microsoft's US data centers could use
  about 700,000 liters of fresh water for cooling.
- Projected that AI could account for 4.2 to 6.6 billion cubic meters of
  water withdrawal worldwide in 2027.
- Connection: the main source for the claim that more AI training uses more
  water. This project measured training data and time, not water, and uses
  this paper to connect the two.

## Not found

No published study found that trains many copies of the same NFL predictor
on different amounts of past data and connects the result to computing and
water use. That doesn't prove nobody has done it, so in the paper say "I did
not find a study that...", not "this has never been done".

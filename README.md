This is a very brief outline of the Project. For more information please refer to docs/report/final_Report.pdf.
Replicate.ipynb contains the code used to obtain the results below.
Collect.ipynb cotains the code used to fetch and process the data.


## Problem

The goal of my project is to efficiently predict which NBA basketball players will have the most fantasy points on a given game. While this can be done with almost any sports, I focused on fantasy NBA due to the abundance of websites simulating it and the fact that I have some knowledge of the sport. While this kind of game is most of time compared to gambling, there exist a few numbers of \textit{professional players} who have proven it is possible to win in the long term given the correct algorithms.

## Data

The data was collected from the http://stats.nba.com/ website and contains the statistics of every game for each player considered.

## Next Game Prediction
A simple linear regression is used on normalized features.

The results were computed using different methods :
- Sliding Average
- Using a binary vector representing position
- Using location average (depending on wether next game is home or away
- Using average of last games

In order to evaluate the model I use the average error made as well as the maximum error. For now I assume the seasons are independent and use all but one k-folding (testing on one season, training on the rest, repeat for each season) to generate an error value. As a baseline I predict a fantasy score for a given game to be equal to the score of the last game.

## Results

When the training and testing sets are computed in the same way I obtain the following results using a dataset of 10 seasons (from 2005 to 2016) with removal of season 2011-12:

| Method       |            | All players   | Linear (Normalized) | Best 120 players after 1.5 months |               |
|--------------|------------|---------------|---------------------|-----------------------------------|---------------|
|              | Mean Error | Maximum Error |                     | Mean Error                        | Maximum Error |
| Baseline     | 7.35       | 48.44         |                     | 8.88                              | 48.33         |
| Baseline(avg)| 5.69       | 39.62         |                     | 6.71                              | 38.01         |
| Slide        | 5.69       | 38.87         |                     | 6.66                              | 37.69         |
| Bslide       | 5.69       | 38.90         |                     | 6.66                              | 37.68         |
| slide_loc    | 5.69       | 38.81         |                     | 6.65                              | 37.30         |
| slide_5      | 5.63       | 38.47         |                     | 6.63                              | 37.47         |
| slide_10     | 5.64       | 38.13         |                     | 6.63                              | 37.48         |
| slide_3      | 5.63       | 38.56         |                     | 6.63                              | 37.53         |
| Bslide_5     | 5.63       | 38.52         |                     | 6.63                              | 37.44         |
| Bslide_loc_5 | 5.64       | 38.35         |                     | 6.62                              | 37.04         |
| slide_loc_5  | 5.64       | 38.26         |                     | 6.62                              | 36.94         |
| Bslide_7     | 5.63       | 38.30         |                     | 6.62                              | 36.97         |

Note that a game value range roughly from -3 to 65

## Simulation
The second method consisted in not predicting the next game but the score on the next week. The seasons are not considered independant (the training is only in the past) and the model is retrained every week with the additionnal games played. A linear model is used on polynomial features. The average error per week goes from 11.08 when testing on the 2006-07 season (one season as initial training) down to 10.02 when testing on the 2015-16 season (9 seasons of initial training).

My implementation can produce a given number of players to select for each week and compares them to the best players possible.

For example : 

| Players Predicted | Predicted Score | Actual Score | Best Players      | Score |
|-------------------|-----------------|--------------|-------------------|-------|
| Blake Griffin     | 120             | 144          | Blake Griffin     | 144   |
| James Harden      | 111             | 134          | James Harden      | 134   |
| Paul Millsap      | 110             | 133          | Paul Millsap      | 133   |
| DeAndreJordan     | 103             | 93           | Stephen Curry     | 123   |
| Stephen Curry     | 103             | 123          | Kawhi Leonard     | 118   |
| Andre Drummond    | 99              | 92           | Chris Paul        | 113   |
| Chris Paul        | 92              | 113          | Draymond Green    | 104   |
| Al Horford        | 92              | 84           | Kevin Durant      | 104   |
| Dwight Howard     | 88              | 69           | Paul George       | 97    |
| Isaiah Thomas     | 87              | 80           | DeAndre Jordan    | 93    |
| Greg Monroe       | 87              | 68           | Andre Drummond    | 92    |
| Jeff Teague       | 85              | 84           | Jared Sullinger   | 90    |
| Russell Westbrook | 85              | 77           | Anthony Davis     | 90    |
| Rajon Rondo       | 83              | 70           | Al Horford        | 84    |
| Kawhi Leonard     | 81              | 118          | Jeff Teague       | 84    |
| Draymond Green    | 80              | 104          | Isaiah Thomas     | 80    |
| Jared Sullinger   | 80              | 90           | Kevin Love        | 79    |
| LaMarcus Aldridge | 79              | 58           | LeBron James      | 77    |
| Anthony Davis     | 78              | 90           | Russell Westbrook | 77    |
| Kevin Durant      | 76              | 104          | Reggie Jackson    | 76    |
| Total             | 1817            | 1928         |                   | 1992  |

On the best week of the 2015-16 season only 4 of the 20 players predicted should not be there.

## Future Work

- Refactor and optimize code
- Use team Statistics
- Remove useless features
- Use expert's opinions


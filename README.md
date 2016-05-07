This is a very brief outline of the Project. For more information please refer to report/Mid_Report.pdf.
Replicate.ipynb contains the code use to obtain the results below (except for the baseline)
Collect.ipynb cotains the code used to fetch and process the data.


## Problem

The goal of my project is to efficiently predict which NBA basketball players will have the most fantasy points on a given game. While this can be done with almost any sports, I focused on fantasy NBA due to the abundance of websites simulating it and the fact that I have some knowledge of the sport. While this kind of game is most of time compared to gambling, there exist a few numbers of \textit{professional players} who have proven it is possible to win in the long term given the correct algorithms.

## Data

The data was collected from the http://stats.nba.com/ website and contains the statistics of every game for each player considered.

## Methods
A simple linear regression is used on the features.

The results were computed following 4 different methods :
- Raw averages
- Sliding Average
- Weighted Sliding Average
- Doubling number of features by considering the location of the game

In order to evaluate the model I use the average error made as well as the maximum error. For nowI assume the seasons are independent and use all but one k-folding (testing on one season, trainingon the rest, repeat for each season) to generate an error value. As a baseline I predict a fantasy score for a given game to be equal to the score of the last game.

## Results

When the training and testing sets are computed in the same way I obtain the following resultsusing a dataset of 9 seasons (from 2005 to 2014):

| Method                   | Mean Error | Maximum Error |
|--------------------------|------------|---------------|
| Baseline                 | 5.23       | 36.22         |
| Raw                      | 5.14       | 25.00         |
| Sliding                  | 4.27       | 30.70         |
| Weighted_Sliding (w = 2) | 4.29       | 30.85         |
| Double_Instances         | 4.32       | 31.26         |

Normalizing the features provides very similar results.

## Future Work

- Correct some code mistakes and refactor
- Change model
- Include other features
- Use expert's opinions


This is a very brief outline of the Project. For more information please refer to docs/report/Mid_Report.pdf.
Replicate.ipynb contains the code use to obtain the results below (except for the baseline).
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

When the training and testing sets are computed in the same way I obtain the following results using a dataset of 10 seasons (from 2005 to 2015):

|              |            |               | Linear Model |            |               |   | Ridge      |               |
|--------------|------------|---------------|--------------|------------|---------------|---|------------|---------------|
|              |            |               |              | Normalized |               |   |            |               |
| Method       | Mean Error | Maximum Error |              | Mean Error | Maximum Error |   | Mean Error | Maximum Error |
| Baseline     | 5.23       | 36.22         |              | 5.23       | 36.22         |   | 5.23       | 36.22         |
| Slide        | 4.29       | 30.32         |              | 4.29       | 30.33         |   | 4.29       | 30.33         |
| Bslide       | 4.29       | 30.31         |              | 4.29       | 30.31         |   | 4.29       | 30.32         |
| slide_loc    | 4.29       | 30.33         |              | 4.29       | 30.32         |   | 4.29       | 30.32         |
| slide_5      | 4.17       | 28.89         |              | 4.17       | 28.89         |   | 4.17       | 28.93         |
| slide_10     | 4.19       | 29.57         |              | 4.19       | 29.55         |   |            |               |
| slide_3      | 4.17       | 29.07         |              | 4.17       | 29.07         |   |            |               |
| Bslide_5     | 4.17       | 28.86         |              | 4.18       | 28.87         |   | 4.17       | 28.92         |
| Bslide_loc_5 | 4.17       | 28.89         |              | 4.17       | 28.91         |   |            |               |
| slide_loc_5  | 4.17       | 28.93         |              | 4.17       | 28.94         |   |            |               |
| Bslide_7     | 4.18       | 29.04         |              | 4.18       | 29.03         |   |            |               |

with correct fantasy calculations :

| Method (Normalized Features) | Mean Error | Maximum Error |
|------------------------------|------------|---------------|
| Baseline                     | 9.74       | 67.7          |
| Slide                        | 7.83       | 53.44         |
| Bslide                       | 7.71       | 53.50         |
| slide_loc                    | 7.83       | 53.44         |
| slide_5                      | 7.64       | 53.47         |
| slide_10                     | 7.68       | 52.92         |
| slide_3                      | 7.63       | 53.28         |
| Bslide_5                     | 7.64       | 53.44         |
| Bslide_loc_5                 | 7.63       | 53.45         |
| slide_loc_5                  | 7.64       | 53.45         |
| Bslide_7                     | 7.64       | 53.65         |

with removal of season 2011-12:

| Method       |            | All players   | Linear (Normalized) | Best 120 players after 1.5 months |               |
|--------------|------------|---------------|---------------------|-----------------------------------|---------------|
|              | Mean Error | Maximum Error |                     | Mean Error                        | Maximum Error |
| Baseline     | 9.77       | 68.44         |                     | 11.52                             | 68.44         |
| Baseline(avg)| 7.89       | 55.93         |                     | 8.88                              | 54.18
| Slide        | 7.83       | 53.31         |                     | 8.81                              | 52.44         |
| Bslide       | 7.83       | 54.29         |                     | 8.81                              | 52.47         |
| slide_loc    | 7.83       | 53.35         |                     | 8.79                              | 52.12         |
| slide_5      | 7.64       | 54.00         |                     | 8.70                              | 52.23         |
| slide_10     | 7.68       | 53.37         |                     | 8.71                              | 51.74         |
| slide_3      | 7.64       | 53.98         |                     | 8.71                              | 52.72         |
| Bslide_5     | 7.65       | 53.96         |                     | 8.70                              | 52.34         |
| Bslide_loc_5 | 7.64       | 54.01         |                     | 8.69                              | 52.19         |
| slide_loc_5  | 7.64       | 54.03         |                     | 8.69                              | 52.05         |
| Bslide_7     | 7.65       | 54.03         |                     | 8.70                              | 51.95         |

## Future Work

- Correct some code mistakes and refactor
- Change model
- Include other features
- Use expert's opinions


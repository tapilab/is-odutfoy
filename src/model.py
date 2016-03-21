from stats import *
import glob
import numpy as np
from sklearn import linear_model

#prepares data to be fit using only raw averages of all games (but the last) of each players
def raw_averages(season):
    averages = []
    next_match_points = []
    players = glob.glob('data' + os.sep + season + os.sep + 'player_stats' + os.sep + "*.pkl")
    for file in players:
        playerID = file[26:-4]
        averages.append(average(season, playerID)[0])
        next_match_points.append(compute_fantasy(season, playerID))
    X = np.array(averages)
    y = np.array(next_match_points)

    return X, y

X, y = raw_averages('2011-12')

lr = linear_model.LinearRegression()

lr.fit(X, y)

def training_error(X,y, model):
    predictions = model.predict(X)
    avg_error = 0.
    max_error = 0.
    for i, prediction in enumerate(predictions):
        error = abs(prediction - y[i])
        avg_error += error
        max_error = error if error > max_error else max_error

    return avg_error/predictions.shape[0], max_error

print training_error(X, y, lr)



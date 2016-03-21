from stats import *
import glob
import numpy as np
from sklearn import linear_model
import matplotlib.pyplot as plt

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

#sliding error using raw averages for one player
def sliding_raw_average(season, playerID):
    averages = []
    next_match_points = []
    player = pickle.load(open('data' + os.sep + season + os.sep + 'player_stats' + os.sep + playerID + '.pkl', 'rb'))
    games_num = len(player['stats'])

    for i in range(1, games_num - 1):
        averages.append(average(season, playerID, i)[0])
        next_match_points.append(compute_fantasy(season, playerID, i + 1))

    X = np.array(averages)
    y = np.array(next_match_points)

    return X, y


def train_linear(X, y, normalize = False):
    lr = linear_model.LinearRegression(normalize=normalize)
    lr.fit(X,y)

    return lr

#X, y = raw_averages('2011-12')
X, y = sliding_raw_average('2011-12', '101107')
print X.shape, y.shape
model = train_linear(X, y)
modeln = train_linear(X, y, True)


#computed error given model an input
def error(model, X, y):
    predictions = model.predict(X)
    avg_error = 0.
    max_error = 0.
    errors = []
    for i, prediction in enumerate(predictions):
        error = abs(prediction - y[i])
        avg_error += error
        max_error = error if error > max_error else max_error
        errors.append(error)

    plt.plot(errors)
    plt.show()

    return avg_error/predictions.shape[0], max_error

print error(model, X, y)
print error(modeln, X, y)










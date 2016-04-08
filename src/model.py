from stats import *
import glob
import numpy as np
from sklearn import linear_model
import matplotlib.pyplot as plt
import shutil

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

    if os.path.exists('data' + os.sep + season + os.sep + 'averages' + os.sep + 'raw_X' + '.pkl'):
        os.remove('data' + os.sep + season + os.sep + 'averages' + os.sep + 'raw_X' + '.pkl')
        os.remove('data' + os.sep + season + os.sep + 'averages' + os.sep + 'raw_y' + '.pkl')

    pickle.dump(X, open('data' + os.sep + season + os.sep + 'averages' + os.sep + 'raw_X' + '.pkl', 'wb'))
    pickle.dump(y, open('data' + os.sep + season + os.sep + 'averages' + os.sep + 'raw_y' + '.pkl', 'wb'))

    return X, y

#sliding average using raw averages for one player
def sliding_average(season, playerID):
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

#sliding averages for all players in one season
def sliding_averages(season):
    Xs = []
    ys = []
    players = glob.glob('data' + os.sep + season + os.sep + 'player_stats' + os.sep + "*.pkl")
    for file in players:
        playerID = file[26:-4]
        X, y = sliding_average(season, playerID)

        if X.shape != (0,):
            Xs.append(X)
            ys.append(y)

    Xf = np.concatenate(Xs)
    yf = np.concatenate(ys)

    if os.path.exists('data' + os.sep + season + os.sep + 'averages' + os.sep + 'sliding_X' + '.pkl'):
        os.remove('data' + os.sep + season + os.sep + 'averages' + os.sep + 'sliding_X' + '.pkl')
        os.remove('data' + os.sep + season + os.sep + 'averages' + os.sep + 'sliding_y' + '.pkl')

    pickle.dump(Xf, open('data' + os.sep + season + os.sep + 'averages' + os.sep + 'sliding_X' + '.pkl', 'wb'))
    pickle.dump(yf, open('data' + os.sep + season + os.sep + 'averages' + os.sep + 'sliding_y' + '.pkl', 'wb'))

    return Xf, yf

#sliding averages for all players in all seasons
# def sliding_averages(seasons):
#     averages = []
#     next_match_points = []
#     for season in seasons:
#         players = glob.glob('data' + os.sep + season + os.sep + 'player_stats' + os.sep + "*.pkl")
#         for file in players:
#             playerID = file[26:-4]
#             player = pickle.load(open('data' + os.sep + season + os.sep + 'player_stats' + os.sep + playerID + '.pkl', 'rb'))
#             games_num = len(player['stats'])
#
#             for i in range(1, games_num - 1):
#                 averages.append(average(season, playerID, i)[0])
#                 next_match_points.append(compute_fantasy(season, playerID, i + 1))
#
#     X = np.array(averages)
#     y = np.array(next_match_points)
#
#     return X, y


def train_linear(X, y, normalize = False):
    lr = linear_model.LinearRegression(normalize=normalize)
    lr.fit(X, y)

    return lr

#computed error given model as input
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

    #plt.plot(errors)
    #plt.show()

    return avg_error/predictions.shape[0], max_error


# X = pickle.load(open('data' + os.sep + '2006-07' + os.sep + 'averages' + os.sep + 'raw_X' + '.pkl', 'rb'))
# y = pickle.load(open('data' + os.sep + '2006-07' + os.sep + 'averages' + os.sep + 'raw_y' + '.pkl', 'rb'))
#
# model = train_linear(X, y)
# modeln = train_linear(X, y, True)
#
# print error(model, X, y)
# print error(modeln, X, y)

#all but one fold error over seasons using sliding raw averages
def ABOF_error(seasons):
    data = map(sliding_averages, seasons)
    errors = []
    avg_error = 0.
    avg_max = 0.

    for i, season in enumerate(seasons):
        print "Testing on season %s (Training on the rest)" % season
        Xs = [dat[0] for dat in data]
        ys = [dat[1] for dat in data]
        testX, testy = Xs.pop(i), ys.pop(i)
        trainX, trainy = np.concatenate(Xs), np.concatenate(ys)
        model = train_linear(trainX, trainy)
        err = error(model, testX, testy)
        errors.append(err[0])
        avg_error += err[0]
        avg_max += err[1]

        print "error for this season is %s" % (err,)

    result = avg_error/len(seasons), avg_max/len(seasons)
    print "Average error and Averaged max error over all seasons is %s" % (result,)

    return result

#seasons = ['2005-06', '2006-07', '2007-08', '2008-09', '2009-10', '2010-11', '2011-12', '2012-13', '2013-14']
#seasons = ['2006-07', '2007-08']
#ABOF_error(seasons)







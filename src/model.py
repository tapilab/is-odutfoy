from stats import *
import glob
import numpy as np
from sklearn import linear_model
import matplotlib.pyplot as plt
import shutil
from plot import *

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
# def sliding_average(season, playerID):
#     averages = []
#     next_match_points = []
#     player = pickle.load(open('data' + os.sep + season + os.sep + 'player_stats' + os.sep + playerID + '.pkl', 'rb'))
#     games_num = len(player['stats'])
#
#     for i in range(1, games_num - 1):
#         averages.append(average(season, playerID, i)[0])
#         next_match_points.append(compute_fantasy(season, playerID, i + 1))
#
#     X = np.array(averages)
#     y = np.array(next_match_points)
#
#     return X, y

#sliding average using weight depending on whether next game is home or away
def sliding_loc_weight_average(season, playerID, weight = 2):
    averages = []
    next_match_points = []
    player = pickle.load(open('data' + os.sep + season + os.sep + 'player_stats' + os.sep + playerID + '.pkl', 'rb'))
    games_num = len(player['stats'])

    for i in range(1, games_num - 1):
        all, home, away = average(season, playerID, i)
        next_match_points.append(compute_fantasy(season, playerID, i + 1))
        #test if next game is home or away
        if player['stats'][i + 1][2][4] == '@':
            avg = weighted_average(home, away, weight)
            averages.append(avg)

        else:
            avg = weighted_average(away, home, weight)
            averages.append(avg)

    X = np.array(averages)
    y = np.array(next_match_points)

    return X, y

#sliding averages for all players in one season using location weighted average
def sliding_averages(season, weight = 2):
    Xs = []
    ys = []
    players = glob.glob('data' + os.sep + season + os.sep + 'player_stats' + os.sep + "*.pkl")
    for file in players:
        playerID = file[26:-4]
        X, y = sliding_loc_weight_average(season, playerID, weight)

        if X.shape != (0,):
            Xs.append(X)
            ys.append(y)

    Xf = np.concatenate(Xs)
    yf = np.concatenate(ys)

    if os.path.exists('data' + os.sep + season + os.sep + 'averages' + os.sep + 'sliding_X' + str(weight) + '.pkl'):
        os.remove('data' + os.sep + season + os.sep + 'averages' + os.sep + 'sliding_X' + str(weight) + '.pkl')
        os.remove('data' + os.sep + season + os.sep + 'averages' + os.sep + 'sliding_y' + str(weight) + '.pkl')

    pickle.dump(Xf, open('data' + os.sep + season + os.sep + 'averages' + os.sep + 'sliding_X' + str(weight) + '.pkl', 'wb'))
    pickle.dump(yf, open('data' + os.sep + season + os.sep + 'averages' + os.sep + 'sliding_y' + str(weight) + '.pkl', 'wb'))

    return Xf, yf

#sliding average with twice as many features (one general and one H/A)
def sliding_loc_average(season, playerID):
    averages = []
    next_match_points = []
    player = pickle.load(open('data' + os.sep + season + os.sep + 'player_stats' + os.sep + playerID + '.pkl', 'rb'))
    games_num = len(player['stats'])

    for i in range(1, games_num - 1):
        all, home, away = average(season, playerID, i)
        points = compute_fantasy(season, playerID, i + 1)
        next_match_points.append(points)
        averages.append(all)

        #test if next game is home or away
        if player['stats'][i + 1][2][4] == '@' and home != []:
            next_match_points.append(points)
            averages.append(home)


        elif away != []:
            next_match_points.append(points)
            averages.append(away)

    X = np.array(averages)
    y = np.array(next_match_points)

    return X, y

def sliding_loc_averages(season):
    Xs = []
    ys = []
    players = glob.glob('data' + os.sep + season + os.sep + 'player_stats' + os.sep + "*.pkl")
    for file in players:
        playerID = file[26:-4]
        X, y = sliding_loc_average(season, playerID)

        if X.shape != (0,):
            Xs.append(X)
            ys.append(y)

    Xf = np.concatenate(Xs)
    yf = np.concatenate(ys)

    if os.path.exists('data' + os.sep + season + os.sep + 'averages' + os.sep + 'sliding_loc_X' + '.pkl'):
        os.remove('data' + os.sep + season + os.sep + 'averages' + os.sep + 'sliding_loc_X' + '.pkl')
        os.remove('data' + os.sep + season + os.sep + 'averages' + os.sep + 'sliding_loc_yc' + '.pkl')

    pickle.dump(Xf, open('data' + os.sep + season + os.sep + 'averages' + os.sep + 'sliding_loc_X' + '.pkl', 'wb'))
    pickle.dump(yf, open('data' + os.sep + season + os.sep + 'averages' + os.sep + 'sliding_loc_y' + '.pkl', 'wb'))

    return Xf, yf

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

# X = pickle.load(open('data' + os.sep + '2006-07' + os.sep + 'averages' + os.sep + 'sliding_X' + '.pkl', 'rb'))
# y = pickle.load(open('data' + os.sep + '2006-07' + os.sep + 'averages' + os.sep + 'sliding_y' + '.pkl', 'rb'))
#
# model = train_linear(X, y)
# modeln = train_linear(X, y, True)
#
# #testX = pickle.load(open('data' + os.sep + '2013-14' + os.sep + 'averages' + os.sep + 'raw_X' + '.pkl', 'rb'))
# #testy = pickle.load(open('data' + os.sep + '2013-14' + os.sep + 'averages' + os.sep + 'raw_y' + '.pkl', 'rb'))
#
# print error(model, X, y)
# print error(modeln, X, y)

#all but one fold error over seasons using inputed average type (raw, sliding, ...)
def ABOF_error(seasons, average_type = "raw", weight = ""):
    Xs = []
    ys = []
    for season in seasons:
        X = pickle.load(open('data' + os.sep + season + os.sep + 'averages' + os.sep + average_type + '_X' + weight + '.pkl', 'rb'))
        y = pickle.load(open('data' + os.sep + season + os.sep + 'averages' + os.sep + average_type + '_y' + weight + '.pkl', 'rb'))
        Xs.append(X)
        ys.append(y)

    errors = []
    avg_error = 0.
    avg_max = 0.

    errorsn = []
    avg_errorn = 0.
    avg_maxn = 0.

    for i, season in enumerate(seasons):
        print "Testing on season %s (Training on the rest)" % season
        tmp_X = list(Xs)
        tmp_y = list(ys)
        testX, testy = tmp_X.pop(i), tmp_y.pop(i)
        trainX, trainy = np.concatenate(tmp_X), np.concatenate(tmp_y)
        model = train_linear(trainX, trainy)
        modeln = train_linear(trainX, trainy, True)
        err = error(model, testX, testy)
        errn = error(modeln, testX, testy)
        errors.append(err[0])
        errorsn.append(errn[0])
        avg_error += err[0]
        avg_errorn += errn[0]
        avg_max += err[1]
        avg_maxn += errn[1]

        plot(trainX, trainy)

        print "error for this season is %s" % (err,)
        print "error for this season with normalized features is %s" % (errn,)



    result = avg_error/len(seasons), avg_max/len(seasons)
    resultn = avg_errorn/len(seasons), avg_maxn/len(seasons)
    print "Average error and Averaged max error over all seasons is %s" % (result,)
    print "Average error and Averaged max error over all seasons with normalized features is %s" % (resultn,)


    return result, resultn


seasons = ['2005-06', '2006-07', '2007-08', '2008-09', '2009-10', '2010-11', '2011-12', '2012-13', '2013-14']
ABOF_error(seasons, "sliding_loc", "")

# for season in seasons:
#      print season
#      sliding_loc_averages(season)

#baselines(seasons)

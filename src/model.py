from stats import *
import glob
import numpy as np
from sklearn import linear_model
import matplotlib.pyplot as plt
import shutil
from plot import *

#factored code to compute sliding feature matrices for one player
def player_features(season, playerID, binary_pos = False, include_loc = False, include_pos = False, include_last_games = False, num_last_games = 0):
    averages = []
    next_match_points = []
    player = pickle.load(open('data' + os.sep + season + os.sep + 'player_stats' + os.sep + playerID + '.pkl', 'rb'))
    games_num = len(player['stats'])

    for i in range(1, games_num - 1):
        all, home, away = average(season, player, i)

        tmp = list(all)

        if binary_pos:
            positions = ['Center', 'Forward', 'Center-Forward', 'Guard', 'Forward-Guard', 'Forward-Center', 'Guard-Forward']
            index = positions.index(player["position"])
            bin = [0, 0, 0, 0, 0, 0, 0]
            bin[index] += 1

            tmp = bin + tmp

        if include_loc:
            #test if next game is home or away
            if player['stats'][i + 1][2][4] == '@':
                #To make sure features exist
                if home != []:
                    tmp += home
                else:
                    continue

            else:
                if away != []:
                    tmp += away
                else:
                    continue

        #TODO : if include_pos: (See notes for question)

        if include_last_games:
            last = average(season, player, i, i - num_last_games)[0]
            tmp += last

        averages.append(tmp)
        next_match_points.append(compute_fantasy(season, player, i + 1))

    X = np.array(averages)
    y = np.array(next_match_points)

    return X, y

#factored code to compute sliding feature matrices for one season
def season_features(season, binary_pos = False, include_loc = False, include_pos = False, include_last_games = False, num_last_games = 0):
    Xs = []
    ys = []
    players = glob.glob('data' + os.sep + season + os.sep + 'player_stats' + os.sep + "*.pkl")
    for file in players:
        playerID = file[26:-4]
        #print "Dealing with {}".format(playerID)
        X, y = player_features(season, playerID, binary_pos, include_loc, include_pos, include_last_games, num_last_games)

        if X.shape != (0,):
            Xs.append(X)
            ys.append(y)

    Xf = np.concatenate(Xs)
    yf = np.concatenate(ys)

    filename = 'slide'

    if binary_pos:
        filename = 'B' + filename

    if include_loc:
        filename += '_loc'

    if include_pos:
        filename += '_pos'

    if include_last_games:
        filename += '_' + str(num_last_games)

    if os.path.exists('data' + os.sep + season + os.sep + 'averages' + os.sep + filename + '_X.pkl'):
        os.remove('data' + os.sep + season + os.sep + 'averages' + os.sep + filename + '_X.pkl')
        os.remove('data' + os.sep + season + os.sep + 'averages' + os.sep + filename + '_y.pkl')

    pickle.dump(Xf, open('data' + os.sep + season + os.sep + 'averages' + os.sep + filename + '_X.pkl', 'wb'))
    pickle.dump(yf, open('data' + os.sep + season + os.sep + 'averages' + os.sep + filename + '_y.pkl', 'wb'))

    return Xf, yf


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

#sliding average with twice as many features (one general and one H/A) for the whole season
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
def ABOF_error(seasons, model, binary_pos = False, include_loc = False, include_pos = False, include_last_games = False, num_last_games = 0):
    filename = 'slide'

    if binary_pos:
        filename = 'B' + filename

    if include_loc:
        filename += '_loc'

    if include_pos:
        filename += '_pos'

    if include_last_games:
        filename += '_' + str(num_last_games)

    Xs = []
    ys = []

    for season in seasons:
        X = pickle.load(open('data' + os.sep + season + os.sep + 'averages' + os.sep + filename + '_X.pkl', 'rb'))
        y = pickle.load(open('data' + os.sep + season + os.sep + 'averages' + os.sep + filename + '_y.pkl', 'rb'))
        Xs.append(X)
        ys.append(y)

    errors = []
    avg_error = 0.
    avg_max = 0.

    for i, season in enumerate(seasons):
        print "Testing on season %s (Training on the rest)" % season
        tmp_X = list(Xs)
        tmp_y = list(ys)
        testX, testy = tmp_X.pop(i), tmp_y.pop(i)
        trainX, trainy = np.concatenate(tmp_X), np.concatenate(tmp_y)
        model.fit(trainX, trainy)
        err = error(model, testX, testy)
        errors.append(err[0])
        avg_error += err[0]
        avg_max += err[1]

        #print model.coef_

        #plot(trainX, trainy)

        print "error for this season is %s" % (err,)

    result = avg_error/len(seasons), avg_max/len(seasons)
    print "Average error and Averaged max error over all seasons is %s" % (result,)

    print filename
    return result

seasons = ['2005-06', '2006-07', '2007-08', '2008-09', '2009-10', '2010-11', '2011-12', '2012-13', '2013-14', '2014-15']


for season in seasons:
   print season
   #season_features(season, binary_pos=True, include_loc=False, include_pos=False, include_last_games=True, num_last_games=7)

#model = linear_model.LinearRegression(normalize=True)
model = linear_model.Ridge(normalize=False)
ABOF_error(seasons, model, binary_pos=True, include_loc=True, include_pos=False, include_last_games=True, num_last_games=5)

#baselines(seasons)

#season_features("2014-15", binary_pos = False, include_loc = False, include_last_games= False, num_last_games=5)
#
#X = pickle.load(open('data' + os.sep + "2014-15" + os.sep + 'averages' + os.sep + "slide" + '_X.pkl', 'rb'))
#y = pickle.load(open('data' + os.sep + "2014-15" + os.sep + 'averages' + os.sep + "slide" + '_y.pkl', 'rb'))
#
#print X.shape
#print y.shape

#print X[155]
from stats import *
import glob
import numpy as np
from sklearn import linear_model
import matplotlib.pyplot as plt
import shutil
from plot import *
from sklearn import preprocessing
from sklearn import svm
from experts import *

#factored code to compute sliding feature matrices for one player
def player_features(season, playerID, binary_pos = False, include_loc = False, num_last_games = 0, start = 1, end = -1):
    averages = []
    next_match_points = []
    player = pickle.load(open('data' + os.sep + season + os.sep + 'player_stats' + os.sep + playerID + '.pkl', 'rb'))

    if end == -1:
        end = len(player['stats']) - 1

    for i in range(start, end):
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

        if num_last_games > 0:
            last = average(season, player, i, i - num_last_games)[0]
            tmp += last

        tmp.append(i)
        averages.append(tmp)
        next_match_points.append(compute_fantasy(player, i + 1))

    X = np.array(averages)
    y = np.array(next_match_points)

    return X, y

#factored code to compute sliding feature matrices for one season
def season_features(season, binary_pos = False, include_loc = False, num_last_games = 0, best_players = 0):
    Xs = []
    ys = []

    if best_players == 0:
        players = glob.glob('data' + os.sep + season + os.sep + 'player_stats' + os.sep + "*.pkl")

    else:
        best = get_fantasies(season, 'OCT 20, ' + season[:4], 'DEC 15, ' + season[:4])
        players = []

        for player in best[:best_players]:
            players.append(player[0])

    for player in players:
        playerID = player[26:-4] if best_players == 0 else player

        #print "Dealing with {}".format(playerID)
        X, y = player_features(season, playerID, binary_pos, include_loc, num_last_games)

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

    if num_last_games > 0:
        filename += '_' + str(num_last_games)

    if os.path.exists('data' + os.sep + season + os.sep + 'averages' + os.sep + filename + '_X.pkl'):
        os.remove('data' + os.sep + season + os.sep + 'averages' + os.sep + filename + '_X.pkl')
        os.remove('data' + os.sep + season + os.sep + 'averages' + os.sep + filename + '_y.pkl')

    pickle.dump(Xf, open('data' + os.sep + season + os.sep + 'averages' + os.sep + filename + '_X.pkl', 'wb'))
    pickle.dump(yf, open('data' + os.sep + season + os.sep + 'averages' + os.sep + filename + '_y.pkl', 'wb'))

    return Xf, yf

#computed error given model as input
def error(model, X, y):
    predictions = model.predict(X)
    avg_error = 0.
    max_error = 0.
    errors = []
    games = []
    values = [0.]*82
    counter = [0.]*82

    for game, (i, prediction) in zip(X, enumerate(predictions)):
        amount = int(game[-1])
        error = abs(prediction - y[i])
        avg_error += error
        max_error = error if error > max_error else max_error
        errors.append(error)
        games.append(amount)
        values[amount] += error
        counter[amount] += 1

    for i in range(82):
        values[i] = values[i]/counter[i] if counter[i] != 0 else 0

    #plt.plot(values)
    #plt.plot(errors, games, 'o')
    #plt.show()

    return avg_error/predictions.shape[0], max_error


#all but one fold error over seasons using inputed average type (raw, sliding, ...)
def ABOF_error(seasons, model, degree = 0, binary_pos = False, include_loc = False, num_last_games = 0):
    def polyf(X):
        poly = preprocessing.PolynomialFeatures(degree)
        return poly.fit_transform(X)

    filename = 'slide'

    if binary_pos:
        filename = 'B' + filename

    if include_loc:
        filename += '_loc'

    if num_last_games > 0:
        filename += '_' + str(num_last_games)

    Xs = []
    ys = []

    for season in seasons:
        #print season
        X = pickle.load(open('data' + os.sep + season + os.sep + 'averages' + os.sep + filename + '_X.pkl', 'rb'))
        y = pickle.load(open('data' + os.sep + season + os.sep + 'averages' + os.sep + filename + '_y.pkl', 'rb'))

        if degree > 0:
            X = polyf(X)

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

        print trainX.shape

        # if degree > 0:
        #     print "coucou"
        #     trainX = polyf(trainX)
        #     testX = polyf(testX)

        model.fit(trainX, trainy)
        #print model.coef_
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

def compute_and_results(seasons, model, degree=0, binary_pos=False, include_loc=False, num_last_games=0, best_players = 0):
    for season in seasons:
        print season
        season_features(season, binary_pos, include_loc, num_last_games, best_players)
    ABOF_error(seasons, model, degree, binary_pos, include_loc, num_last_games)

#got rid of season 2011-12 because it starts much later
seasons = ['2005-06', '2006-07', '2007-08', '2008-09', '2009-10', '2010-11', '2012-13', '2013-14', '2014-15']

#model = linear_model.SGDRegressor(learning_rate='constant', eta0=0.000001)
#model = linear_model.LinearRegression(normalize=True)
#model = linear_model.Ridge(normalize=True)
#model = svm.SVR(kernel='poly', degree=1, max_iter=5000)

#compute_and_results(seasons, model, degree=0, binary_pos=False, include_loc=False, num_last_games=0, best_players= 0)
#ABOF_error(seasons, model, degree=0, binary_pos=False, include_loc=False, num_last_games=0)
#baselines(seasons, best_players = 120)

# filename = "slide"
# X = pickle.load(open('data' + os.sep + 'sample_' + os.sep + 'averages' + os.sep + filename + '_X.pkl', 'rb'))
# y = pickle.load(open('data' + os.sep + 'sample_' + os.sep + 'averages' + os.sep + filename + '_y.pkl', 'rb'))
#
# #poly = preprocessing.PolynomialFeatures(2)
# #test = poly.fit_transform(X)
#
# #print test.shape
#
# #model.fit(X, y)
# #print error(model, X, y)

#print X[10]


#season_features("2014-15", binary_pos = False, include_loc = False, include_last_games= False, num_last_games=5)
#
#X = pickle.load(open('data' + os.sep + "2014-15" + os.sep + 'averages' + os.sep + "slide" + '_X.pkl', 'rb'))
#y = pickle.load(open('data' + os.sep + "2014-15" + os.sep + 'averages' + os.sep + "slide" + '_y.pkl', 'rb'))
#
#print X.shape
#print y.shape

#print X[155]

#baselines(seasons, best_players=120, avg=True)
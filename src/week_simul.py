from model import *

#builds feature vector for week predition
#start and end are the dates of the week to be predicted, stats of player before start date will be used for prediction
def week_feature(player, start_date, end_date, season_start, binary_pos = False, num_last_games = 0):
    start, end = get_games_num(player, start_date, end_date)

    next_games = get_games(player, start_date, end_date)

    #score = -100 means no games were played by the player the following week and the feature will not be used
    score = 0. if next_games != [] else -100.

    avg = []

    if start > 0:
        avg = average(player, start - 1)[0]

        if binary_pos:
            positions = ['Center', 'Forward', 'Center-Forward', 'Guard', 'Forward-Guard', 'Forward-Center', 'Guard-Forward']
            index = positions.index(player["position"])
            bin = [0, 0, 0, 0, 0, 0, 0]
            bin[index] += 1

            avg = bin + avg

        if num_last_games > 0:
            last = average(player, start - 1, start - 1 - num_last_games)[0]
            avg += last

        for game in next_games:
            score += get_fantasy(game)

        avg.append(start - 1)

        games = get_games(player, season_start, date_sub(start_date, 1))
        avg_points = 0.
        for game in games:
            avg_points += get_fantasy(game)

        if len(games) != 0:
            avg_points = avg_points/len(games)

        avg.append(avg_points)
        avg.append(len(next_games))

    return avg, score

#produces the feature matrix for a entire season wih given step in between 2 dates
def week_features(season, start_date, end_date, step, binary_pos = False, num_last_games = 0, best_players = 0):
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
        player = pickle.load(open('data' + os.sep + season + os.sep + 'player_stats' + os.sep + playerID + '.pkl', 'rb'))
        curr_date = date_add(start_date, step)
        curr_end_date = date_add(curr_date, step)
        while date_before(date_add(curr_end_date, step + 1), end_date):
            X, y = week_feature(player, curr_date, curr_end_date, start_date, binary_pos, num_last_games)

            #make sure some games are played the next week
            if X != [] and y != -100:
                Xs.append(X)
                ys.append(y)

            curr_date = date_add(curr_date, step + 1)
            curr_end_date = date_add(curr_end_date, step + 1)

    Xf = np.reshape(Xs, (len(Xs), len(Xs[0])))
    yf = np.reshape(ys, len(ys))

    return Xf, yf


class week_simul:

    def __init__(self, season, start_date, end_date, model, days = 6, players_num = 0, binary_pos = False, num_last_games = 0, best_players = 0, predict_num = 0):
        print "Initializing attributes"
        self.season = season
        self.curr_date = start_date
        self.prev_seasons = []
        self.model = model
        self.days = days
        self.players_num = players_num
        self.binary_pos = binary_pos
        self.num_last_games = num_last_games
        self.end_date = end_date
        self.week = 0
        self.start_date = start_date
        self.poly = preprocessing.PolynomialFeatures(2)
        self.predict_num = predict_num
        self.week_avg_errors = []
        self.week_max_errors = []

        if self.players_num == 0:
            self.players = glob.glob('data' + os.sep + self.season + os.sep + 'player_stats' + os.sep + "*.pkl")

        else:
            print "Gathering list of best players"
            best = get_fantasies(self.season, 'OCT 20, ' + self.season[:4], 'DEC 15, ' + self.season[:4])
            self.players = []

            for player in best[:self.players_num]:
                self.players.append(player[0])

        #ensuring training data will only be in the past
        for s, s_start, s_end in zip(seasons, start_dates, end_dates):
            year = int(self.season[:4])
            if int(s[:4]) < year:
                self.prev_seasons.append((s, s_start, s_end))

        #creating initial training data
        Xs = []
        ys = []

        print "Building training data"
        for season in self.prev_seasons:
            print season
            X, y = week_features(season[0], season[1], season[2], self.days, self.binary_pos, self.num_last_games, best_players)
            X = self.poly.fit_transform(X)

            Xs.append(X)
            ys.append(y)

        self.trainX, self.trainy = np.concatenate(Xs), np.concatenate(ys)
        print self.trainX.shape, self.trainy.shape
        print self.trainy.min(), self.trainy.max()

        print "Building initial test data"
        next_date = date_add(self.curr_date, self.days)
        self.curr_date = date_add(next_date, 1)
        self.week += 1
        self.update_testing()

    def debug(self):
        print self.season
        print self.curr_date
        print self.prev_seasons
        print self.model
        print self.days
        print len(self.players)
        print self.trainX.shape, self.trainy.shape
        print self.testX.shape, self.testy.shape

    def update_testing(self):
        Xs = []
        ys = []
        next_date = date_add(self.curr_date, self.days)
        for player in self.players:
            playerID = player[26:-4] if self.players_num == 0 else player
            player = pickle.load(open('data' + os.sep + self.season + os.sep + 'player_stats' + os.sep + playerID + '.pkl', 'rb'))
            X, y = week_feature(player, self.curr_date, next_date, self.start_date, self.binary_pos, self.num_last_games)

            if X != [] and y != -100:
                Xs.append(X)
                ys.append(y)

        if len(Xs) != 0:
            self.testX, self.testy = np.reshape(Xs, (len(Xs), len(Xs[0]))), np.reshape(ys, len(ys))
            self.testX = self.poly.fit_transform(self.testX)


    #predicts values and updates training and testing set for the next days
    def simulate(self):
        next_date = date_add(self.curr_date, self.days)
        self.model.fit(self.trainX, self.trainy)
        errors = error(self.model, self.testX, self.testy)

        print "Average and max errors on predictions from {} to {} is {}".format(self.curr_date, next_date, errors)

        self.week_avg_errors.append(errors[0])
        self.week_max_errors.append(errors[1])

        self.trainX, self.trainy = np.concatenate((self.trainX, self.testX)), np.concatenate((self.trainy, self.testy))

        self.curr_date = date_add(next_date, 1)
        self.week += 1

        print "Average error per week so far is {}, {}".format(np.mean(self.week_avg_errors), np.mean(self.week_max_errors))

        if date_before(self.curr_date, self.end_date):
            self.update_testing()

        else:
            print "Season has ended, user should stop simulating"
            coefs = dict()
            for i, coef in enumerate(model.coef_):
                coefs[str(i)] = coef
            print sorted(coefs.items(), key=operator.itemgetter(1), reverse = True)

        return errors

    #produces list of best players and compares to best doable.
    def predict(self):
        next_date = date_add(self.curr_date, self.days)
        self.model.fit(self.trainX, self.trainy)

        predicted = dict()
        scores = dict()

        Xs = []
        ys = []

        for player in self.players:
            playerID = player[26:-4] if self.players_num == 0 else player
            player = pickle.load(open('data' + os.sep + self.season + os.sep + 'player_stats' + os.sep + playerID + '.pkl', 'rb'))
            X, y = week_feature(player, self.curr_date, next_date, self.start_date, self.binary_pos, self.num_last_games)

            if X != [] and y != -100:
                X = np.reshape(X, (1, len(X)))
                X = self.poly.fit_transform(X)
                predicted[player['name']] = model.predict(X)
                scores[player['name']] = y

                #to update training
                Xs.append(X)
                ys.append(y)

        #testX and y are not really used here but useful to update training
        self.testX, self.testy = np.reshape(Xs, (len(Xs), Xs[0].shape[1])), np.reshape(ys, len(ys))
        self.trainX, self.trainy = np.concatenate((self.trainX, self.testX)), np.concatenate((self.trainy, self.testy))

        best_predicted = sorted(predicted.items(), key=operator.itemgetter(1), reverse = True)[:self.predict_num]
        best_real = sorted(scores.items(), key=operator.itemgetter(1), reverse = True)[:self.predict_num]
        predicted_real = []
        for candidate in best_predicted:
            name = candidate[0]
            predicted_real.append((name, scores[name]))

        print "Predictions from {} to {} are as follows : \n".format(self.curr_date, next_date)

        print 'players predicted :\n'
        print best_predicted
        print '\nTheir real score :\n'
        print predicted_real
        print '\nActual best players :\n'
        print best_real

        predicted_score = sum(x[1] for x in best_predicted)
        best_score = sum(x[1] for x in best_real)
        actual_score = sum(x[1] for x in predicted_real)

        print "\nPredicted score : {}".format(predicted_score[0])
        print "Actual score : {}".format(actual_score)
        print "best possible score : {}".format(best_score)

        self.curr_date = date_add(next_date, 1)
        self.week += 1

        if not date_before(self.curr_date, self.end_date):
            print "Season has ended, user should stop simulating"

        return best_score - actual_score

    def full_prediction(self):
        errors = []
        weeks = []

        while date_before(self.curr_date, self.end_date):
            errors.append(self.predict())
            weeks.append(self.week)

        plt.plot(weeks, errors)
        plt.show()

        print "Total error for the {} season is {} which averages to {} a week".format(self.season, sum(errors), np.mean(errors))


    def full_simulation(self, playerID = None):
        errors = []
        weeks = []

        if playerID:
            Xs = []
            ys = []
            player = pickle.load(open('data' + os.sep + self.season + os.sep + 'player_stats' + os.sep + playerID + '.pkl', 'rb'))
            games = get_games(player, self.start_date, date_add(self.start_date, self.days))
            score = 0
            for game in games:
                score += get_fantasy(game)

        while date_before(self.curr_date, self.end_date):
            if playerID:
                X, y = week_feature(player, self.curr_date, date_add(self.curr_date, self.days), self.start_date, self.binary_pos, self.num_last_games)

                if X != [] and y != -100:
                    Xs.append(X)
                    ys.append(y)

            errors.append(self.simulate())
            weeks.append(self.week)

        if playerID:
            playerX, playery = np.reshape(Xs, (len(Xs), len(Xs[0]))), np.reshape(ys, len(ys))
            playerX = self.poly.fit_transform(playerX)
            predicts = self.model.predict(playerX)
            bs = (np.insert(playery, 0, score))[:-1]
            bs_avg = np.zeros(len(playery))
            for i in range(len(playery)):
                bs_avg[i] = np.mean(bs[:i + 1])
            games = range(len(playery))
            plt.plot(games, predicts, 'ro', games, playery, 'o', games, bs, 'go', games, bs_avg, 'yo')
            plt.show()
            plt.clf()
            plt.plot(games, abs(predicts - playery), 'r', games, abs(bs - playery), 'g', games, abs(bs_avg - playery), 'y')
            plt.show()
            plt.clf()

        plt.plot(weeks, errors)
        plt.show()


model = linear_model.LinearRegression(normalize=True)
#model = linear_model.Ridge(normalize=True)
#model = svm.SVR(kernel='linear', degree=1, max_iter=20000)
test = week_simul('2015-16', 'OCT 27, 2015', 'APR 13, 2016', model, days=6, binary_pos= False, num_last_games=0, players_num=0, best_players=0, predict_num=20)
test.full_prediction()
#test.full_simulation('201939')

# X, y = week_features('2013-14', 'OCT 29, 2013', 'APR 16, 2014', 6)
# poly = preprocessing.PolynomialFeatures(2)
# test = poly.fit_transform(X)
# # print test == X
# # print X.shape, test.shape
# model.fit(test, y)
# print X.shape
# print y.shape
#
# player = pickle.load(open('data' + os.sep + '2015-16' + os.sep + 'player_stats' + os.sep + '201939' + '.pkl', 'rb'))
# print player['name']
# testX, y = week_feature(player, 'NOV 10, 2015', 'NOV 16, 2015', 'OCT 27, 2015')
# testX = np.reshape(testX, (1, len(testX)))
# testX = poly.fit_transform(testX)
#
# print model.predict(testX)


#print get_fantasies('2013-14', 'OCT 29, 2013', 'APR 16, 2014')

# Xs, ys = [], []
# for season, s_start, s_end in zip(seasons, start_dates, end_dates):
#     print season
#     X, y = week_features(season, s_start, s_end, 6)
#     Xs.append(X)
#     ys.append(y)
#
# trainX, trainy = np.concatenate(Xs), np.concatenate(ys)
# poly = preprocessing.PolynomialFeatures(2)
# trainX = poly.fit_transform(trainX)
# model.fit(trainX, trainy)
#
# players = glob.glob('data' + os.sep + '2015-16' + os.sep + 'player_stats' + os.sep + "*.pkl")
# for file in players:
#     playerID = file[26:-4]
#     player = pickle.load(open('data' + os.sep + '2015-16' + os.sep + 'player_stats' + os.sep + playerID + '.pkl', 'rb'))
#     testX, testy = week_feature(player, 'NOV 10, 2015', 'NOV 16, 2015', 'OCT 27, 2015')
#     if testX != [] and testy != -100:
#         print player['name']
#         testX = np.reshape(testX, (1, len(testX)))
#         testX = poly.fit_transform(testX)
#         print model.predict(testX), testy


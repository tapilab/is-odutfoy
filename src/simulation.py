from model import *


class simulation:

    #here players_num corresponds to the number of players you want to be taken into account for the simulation
    #while best_players is the number of players for the training of previous seasons
    #days is the number of days taken into account for each step of the simulation
    def __init__(self, season, start_date, end_date, model, days = 6, players_num = 0, binary_pos = False, include_loc = False, num_last_games = 0, best_players = 0):
        print "Initializing attributes"
        self.season = season
        self.curr_date = start_date
        self.prev_seasons = []
        self.model = model
        self.days = days
        self.players_num = players_num
        self.binary_pos = binary_pos
        self.include_loc = include_loc
        self.num_last_games = num_last_games
        self.end_date = end_date
        self.week = 0

        if self.players_num == 0:
            self.players = glob.glob('data' + os.sep + self.season + os.sep + 'player_stats' + os.sep + "*.pkl")

        else:
            print "Gathering list of best players"
            best = get_fantasies(self.season, 'OCT 20, ' + self.season[:4], 'DEC 15, ' + self.season[:4])
            self.players = []

            for player in best[:self.players_num]:
                self.players.append(player[0])

        #ensuring training data will only be in the past
        for s in seasons:
            year = int(self.season[:4])
            if int(s[:4]) < year:
                self.prev_seasons.append(s)

        #creating initial training data
        Xs = []
        ys = []

        print "Building training data"
        for season in self.prev_seasons:
            print season
            X, y = season_features(season, self.binary_pos, self.include_loc, self.num_last_games, best_players)

            Xs.append(X)
            ys.append(y)

        self.trainX, self.trainy = np.concatenate(Xs), np.concatenate(ys)

        print "Building initial test data"
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
        for player in self.players:
            playerID = player[26:-4] if self.players_num == 0 else player
            start, end = get_games_num(playerID, self.season, self.curr_date, date_add(self.curr_date, self.days))

            if start != -1:
                X, y = player_features(self.season, playerID, self.binary_pos, self.include_loc, self.num_last_games, start, end)

                if X.shape != (0,):
                    Xs.append(X)
                    ys.append(y)

        self.testX, self.testy = np.concatenate(Xs), np.concatenate(ys)

    #predicts values and updates training and testing set for the next days
    def simulate(self):
        next_date = date_add(self.curr_date, self.days)
        model.fit(self.trainX, self.trainy)
        errors = error(model, self.testX, self.testy)

        print "Average and max errors on predictions from {} to {} is {}".format(self.curr_date, next_date, errors)

        self.trainX, self.trainy = np.concatenate((self.trainX, self.testX)), np.concatenate((self.trainy, self.testy))

        self.curr_date = date_add(next_date, 1)
        self.week += 1

        if date_before(self.curr_date, self.end_date):
            self.update_testing()

        else:
            print "Season has ended, user should stop simulating"

        return errors

    def full_simulation(self, playerID = None):
        errors = []
        weeks = []
        if playerID:
            Xs = []
            ys = []

        while date_before(self.curr_date, self.end_date):
            if playerID:
                start, end = get_games_num(playerID, self.season, self.curr_date, date_add(self.curr_date, self.days))
                if start != -1:
                    X, y = player_features(self.season, playerID, self.binary_pos, self.include_loc, self.num_last_games, start, end)

                    if X.shape != (0,):
                        Xs.append(X)
                        ys.append(y)

            errors.append(self.simulate())
            weeks.append(self.week)

        if playerID:
            playerX, playery = np.concatenate(Xs), np.concatenate(ys)
            predicts = model.predict(playerX)
            games = [game for game in range(len(playery))]
            plt.plot(games, predicts, 'ro', games, playery, 'o')
            plt.show()
            plt.clf()

        plt.plot(weeks, errors)
        plt.show()


model = linear_model.LinearRegression(normalize=True)
test = simulation('2014-15', 'OCT 28, 2014', 'APR 15, 2015', model, players_num=0, best_players=0)
test.full_simulation('203082')


#print get_all_games('2014-15', 'OCT 28, 2014', date_add('OCT 28, 2014', 6))

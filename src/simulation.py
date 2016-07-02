from model import *


class simulation:

    #here players_num corresponds to the number of players you want to be taken into account for the simulation
    #while best_players is the number of players for the training of previous seasons
    def __init__(self, season, start_date, model, players_num = 0, binary_pos = False, include_loc = False, num_last_games = 0, best_players = 0):
        print "Initializing attributes"
        self.season = season
        self.curr_date = start_date
        self.prev_seasons = []
        self.model = model

        if players_num == 0:
            self.players = glob.glob('data' + os.sep + self.season + os.sep + 'player_stats' + os.sep + "*.pkl")

        else:
            print "Gathering list of best players"
            best = get_fantasies(self.season, 'OCT 20, ' + self.season[:4], 'DEC 15, ' + self.season[:4])
            self.players = []

            for player in best[:players_num]:
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
            X, y = season_features(season, binary_pos, include_loc, num_last_games, best_players)

            Xs.append(X)
            ys.append(y)

        self.trainX, self.trainy = np.concatenate(Xs), np.concatenate(ys)

        #creating initial testing data
        Xs = []
        ys = []

        print "Building initial test data"
        for player in self.players:
            playerID = player[26:-4] if players_num == 0 else player
            start, end = get_games_num(playerID, self.season, self.curr_date, date_add(self.curr_date, 6))

            if start != -1:
                X, y = player_features(self.season, playerID, binary_pos, include_loc, num_last_games, start, end)

                if X.shape != (0,):
                    Xs.append(X)
                    ys.append(y)

        self.testX, self.testy = np.concatenate(Xs), np.concatenate(ys)

    def debug(self):
        print self.season
        print self.curr_date
        print self.prev_seasons
        print self.model
        print len(self.players)
        print self.trainX.shape, self.trainy.shape
        print self.testX.shape, self.testy.shape

model = linear_model.LinearRegression(normalize=True)
test = simulation('2014-15', 'OCT 28, 2014', model, 120, best_players=120)
test.debug()

#print get_all_games('2014-15', 'OCT 28, 2014', date_add('OCT 28, 2014', 6))

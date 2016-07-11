from model import *

#builds feature vector for week predition
#start and end are the dates of the week to be predicted, stats of player before start date will be used for prediction
def week_feature(player, start_date, end_date, binary_pos = False, num_last_games = 0):
    start, end = get_games_num(player, start_date, end_date)

    next_games = get_games(player, start_date, end_date)

    #score = -100 means no games were played by the player the following week and the feature will not be used
    score = 0. if next_games != [] else -100.

    avg = []

    if start != -1:
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
            avg.append(start - 1)

        for game in next_games:
            score += get_fantasy(game)

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
            X, y = week_feature(player, curr_date, curr_end_date, binary_pos, num_last_games)

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

    def __init__(self, season, start_date, end_date, model, days = 6, players_num = 0, binary_pos = False, num_last_games = 0, best_players = 0):
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

            Xs.append(X)
            ys.append(y)

        self.trainX, self.trainy = np.concatenate(Xs), np.concatenate(ys)
        print self.trainX.shape, self.trainy.shape
        print self.trainy.min(), self.trainy.max()

        print "Building initial test data"
        self.update_testing()
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
            X, y = week_feature(player, self.curr_date, next_date, self.binary_pos, self.num_last_games)

            if X != [] and y != -100:
                Xs.append(X)
                ys.append(y)

        self.testX, self.testy = np.reshape(Xs, (len(Xs), len(Xs[0]))), np.reshape(ys, len(ys))


    #predicts values and updates training and testing set for the next days
    def simulate(self):
        next_date = date_add(self.curr_date, self.days)
        self.model.fit(self.trainX, self.trainy)
        errors = error(self.model, self.testX, self.testy)

        print "Average and max errors on predictions from {} to {} is {}".format(self.curr_date, next_date, errors)

        self.trainX, self.trainy = np.concatenate((self.trainX, self.testX)), np.concatenate((self.trainy, self.testy))

        self.curr_date = date_add(next_date, 1)
        self.week += 1

        if date_before(self.curr_date, self.end_date):
            self.update_testing()

        else:
            print "Season has ended, user should stop simulating"

        return errors


#model = linear_model.LinearRegression(normalize=True)
model = linear_model.Ridge(normalize=True)
test = week_simul('2006-07', 'OCT 31, 2006', 'APR 18, 2007', model, days=6, binary_pos= False, num_last_games=0, players_num=120, best_players=120)
test.simulate()
test.simulate()
test.simulate()
test.simulate()
test.simulate()
from model import *

#builds feature vector for week predition
#start and end are the week to be predicted, stats of player before start date will be used for prediction
def week_feature(season, player, start, end, binary_pos = False, num_last_games = 0):
    avg = average(season, player, start - 1)[0]

    if binary_pos:
        positions = ['Center', 'Forward', 'Center-Forward', 'Guard', 'Forward-Guard', 'Forward-Center', 'Guard-Forward']
        index = positions.index(player["position"])
        bin = [0, 0, 0, 0, 0, 0, 0]
        bin[index] += 1

        avg = bin + avg

    if num_last_games > 0:
        last = average(season, player, start - 1, start - 1 - num_last_games)[0]
        avg += last
        avg.append(start - 1)

    next_games = get_games(player, start, end)

    score = 0.

    for game in next_games:
        score += get_fantasy(game)

    return avg, score

#produces the feature matrix for a player for the entire season wih given step
def week_features(season, player, start_date, end_date, step, binary_pos = False, num_last_games = 0):


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

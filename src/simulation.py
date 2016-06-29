from model import *

class simulation:

    def __init__(self, season, start_date, curr_date, model, binary_pos = False, include_loc = False, num_last_games = 0, best_players = 0):
        self.season = season
        self.start_date = start_date
        self.curr_date = start_date
        self.prev_seasons = []
        self.model = model

        #ensuring training data will only be in the past
        for s in seasons:
            year = int(season[:4])
            if int(s[:4]) < year:
                self.prev_seasons.append(s)

        #creating initial training data
        Xs = []
        ys = []

        for season in self.prev_seasons:
            print season
            X, y = season_features(season, binary_pos, include_loc, num_last_games, best_players)

            Xs.append(X)
            ys.append(y)

        self.trainX, self.trainy = np.concatenate(Xs), np.concatenate(ys)


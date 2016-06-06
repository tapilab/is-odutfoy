import pickle
import os
import glob
import numpy as np

#This file takes "raw" data as input and computes additionnal stats such as averaged stats, winrate, fatansy points etc.

#Returns the averaged stats (all, home and away) of a given player in his first given number of games as well as winrate
#Returns averaged of all games but last by default
def average(season, player, number_games = -1):
    games_num = len(player['stats'])

    if number_games == 0:
        tmp = [0.]*23
        tmp[21] = player['experience']
        tmp[22] = player['age']
        return tmp, tmp, tmp
        # print "Please choose a strictly positive number of games"
        # exit()

    if number_games == -1:
        return average(season, player, games_num - 1)

    elif number_games > games_num:
        print "not enough games, returned average of all available games (%d)" % games_num
        return average(season, player, games_num)

    else:
        averaged = [float(sum(x))/float(len(x)) for x in zip(*[match[4:] for match in player['stats'][:number_games]])]

        #Ensuring Percentages are correct
        for i in [3, 6, 9]:
            averaged[i] = 0.5 if averaged[i - 1] == 0 else averaged[i - 2]/averaged[i - 1]

        won = float([match[3] for match in player['stats'][:number_games]].count('W'))
        winrate = won/number_games
        averaged.append(winrate)
        averaged.append(player['experience'])
        averaged.append(player['age'])

        home = [match for match in player['stats'][:number_games] if match[2][4] == '@']
        away = [match for match in player['stats'][:number_games] if match[2][4] != '@']

        #In order to avoid unreferenced return
        home_avg = []
        away_avg = []

        if len(home) != 0:
            home_avg = [float(sum(x))/float(len(x)) for x in zip(*[match[4:] for match in home])]

            #Ensuring Percentages are correct
            for i in [3, 6, 9]:
                home_avg[i] = 0.5 if home_avg[i - 1] == 0. else home_avg[i - 2]/home_avg[i - 1]

            home_won = float([match[3] for match in home].count('W'))
            home_winrate = home_won/len(home)
            home_avg.append(home_winrate)
            home_avg.append(player['experience'])
            home_avg.append(player['age'])

        if len(away) != 0:
            away_avg = [float(sum(x))/float(len(x)) for x in zip(*[match[4:] for match in away])]

            #Ensuring Percentages are correct
            for i in [3, 6, 9]:
                away_avg[i] = 0.5 if away_avg[i - 1] == 0 else away_avg[i - 2]/away_avg[i - 1]

            away_won = float([match[3] for match in away].count('W'))
            away_winrate = away_won/len(away)
            away_avg.append(away_winrate)
            away_avg.append(player['experience'])
            away_avg.append(player['age'])

        return averaged, home_avg, away_avg

#print average('2011-12', '201149')

#computes fantasy points of a given player on his given ith game (last by default)
#Allows different way of computing points but has espn values by default
def compute_fantasy(season, player, game_number = -1,
                    PTS = 1, BLK = 1, STL = 1, AST = 1, REB = 1, FGM = 1, FTM = 1, FGA = -1, FTA = -1, TOV = -1):
    games_num = len(player['stats'])

    if game_number == -1:
        return compute_fantasy(season, player, games_num,
                        PTS, BLK, STL, AST, REB, FGM, FTM, FGA, FTA, TOV)

    elif game_number > games_num:
        print "This game does not exist, returned last game played instead"
        return compute_fantasy(season, player, games_num,
                        PTS, BLK, STL, AST, REB, FGM, FTM, FGA, FTA, TOV)

    else:
        game = player['stats'][game_number - 1]
        score = PTS*game[20] + BLK*game[19] + STL*game[18] + AST*game[17] + REB*game[16] + FGM*game[5]
        + FTM*game[11] + FGA*game[6] + FTA*game[12] + TOV*game[20]

        return score

#returns weighted average with avg1 more important than avg by factor of weight
def weighted_average(avg1, avg2, weight = 2):
    if len(avg1) == 0:
        return avg2

    elif len(avg2) == 0:
        return avg1

    avg = []
    for i, a, b, in enumerate(zip(avg1, avg2)):
        #to ensure correct percentages
        if i in [3, 6, 9]:
            tmp = avg[i - 2]/avg[i - 1]

        else:
            tmp = (a*weight + b)/(weight + 1)

        avg.append(tmp)

    return avg

def baseline(season):
    errors = []
    players = glob.glob('data' + os.sep + season + os.sep + 'player_stats' + os.sep + "*.pkl")

    for file in players:
        playerID = file[26:-4]
        player = pickle.load(open('data' + os.sep + season + os.sep + 'player_stats' + os.sep + playerID + '.pkl', 'rb'))
        games_num = len(player['stats'])

        for i in range(1, games_num - 1):
            next_points = compute_fantasy(season, playerID, i + 1)
            curr_points = compute_fantasy(season, playerID, i)
            errors.append(abs(next_points - curr_points))

    error = np.mean(errors), np.max(errors)

    file = open('data' + os.sep + season + os.sep + 'averages' + os.sep + 'baseline.txt', "w")
    file.write("{}".format(error))
    file.close()

    print "Average error and max error for season {} is {}".format(season, error)

    return error

def baselines(seasons):
    avg_error = 0.
    avg_max = 0.

    for season in seasons:
        print "computing for season {}".format(season)
        error = baseline(season)
        avg_error += error[0]
        avg_max += error[1]

    result = avg_error/len(seasons), avg_max/len(seasons)

    print "Average error and Averaged max error over all seasons is %s" % (result,)

    return result

#print compute_fantasy('2011-12', '977', 0)
# positions = []
# for file in os.listdir("data/2006-07/player_stats"):
#     player = pickle.load(open("data/2006-07/player_stats/" + file, 'rb'))
#     position = player['position']
#     if position == 'Forward-Guard':
#         print "FG"
#         print player['name']
#
#     if position == 'Guard-Forward':
#         print "GF"
#         print player['name']
#
#     if position not in positions:
#         positions.append(position)

#print positions
#print average('2005-06', '15')[0]
#print player['stats']
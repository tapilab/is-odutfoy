import pickle
import os
import glob
import numpy as np

#This file takes "raw" data as input and computes additionnal stats such as averaged stats, winrate, fatansy points etc.

#Returns the averaged stats (all, home and away) of a given player between game start and end
#Returns averaged of all games but last by default
def average(season, player, end = -1, start = 0):
    games_num = len(player['stats'])

    experience = player['experience']
    age = player['age']
    height = 6*int(player['height'].split('-')[0]) + int(player['height'].split('-')[1])
    weight = int(player['weight'])

    if end == 0:
        tmp = [0.]*25
        tmp[21] = experience
        tmp[22] = age
        tmp[23] = height
        tmp[24] = weight
        return tmp, tmp, tmp
        # print "Please choose a strictly positive number of games"
        # exit()

    if end == -1:
        return average(season, player, games_num - 1)

    elif end > games_num:
        print "not enough games, returned average of all available games (%d)" % games_num
        return average(season, player, games_num)

    elif start >= end:
        print "start must be smaller then end, returned average of all available games (%d)" % games_num
        return average(season, player, games_num)

    elif start < 0:
        return average(season, player, end)

    else:
        averaged = [float(sum(x))/float(len(x)) for x in zip(*[match[4:] for match in player['stats'][start:end]])]

        #Ensuring Percentages are correct (using average as default value)
        for i, j in zip([3, 6, 9], [0.45, 0.35, 0.75]):
            averaged[i] = j if averaged[i - 1] == 0 else averaged[i - 2]/averaged[i - 1]

        won = float([match[3] for match in player['stats'][start:end]].count('W'))
        winrate = won/end
        averaged.append(winrate)
        averaged.append(experience)
        averaged.append(age)
        averaged.append(height)
        averaged.append(weight)

        home = [match for match in player['stats'][start:end] if match[2][4] == '@']
        away = [match for match in player['stats'][start:end] if match[2][4] != '@']

        #In order to avoid unreferenced return
        home_avg = []
        away_avg = []

        if len(home) != 0:
            home_avg = [float(sum(x))/float(len(x)) for x in zip(*[match[4:] for match in home])]

            #Ensuring Percentages are correct
            for i, j in zip([3, 6, 9], [0.45, 0.35, 0.75]):
                averaged[i] = j if averaged[i - 1] == 0 else averaged[i - 2]/averaged[i - 1]

            home_won = float([match[3] for match in home].count('W'))
            home_winrate = home_won/len(home)
            home_avg.append(home_winrate)
            home_avg.append(experience)
            home_avg.append(age)
            home_avg.append(height)
            home_avg.append(weight)

        if len(away) != 0:
            away_avg = [float(sum(x))/float(len(x)) for x in zip(*[match[4:] for match in away])]

            #Ensuring Percentages are correct
            for i, j in zip([3, 6, 9], [0.45, 0.35, 0.75]):
                averaged[i] = j if averaged[i - 1] == 0 else averaged[i - 2]/averaged[i - 1]

            away_won = float([match[3] for match in away].count('W'))
            away_winrate = away_won/len(away)
            away_avg.append(away_winrate)
            away_avg.append(experience)
            away_avg.append(age)
            away_avg.append(height)
            away_avg.append(weight)

        return averaged, home_avg, away_avg

#print average('2011-12', '201149')

#computes fantasy points of a given player on his given ith game (last by default)
#Allows different way of computing points but has espn values by default
def compute_fantasy(player, game_number = -1,
                    PTS = 1, BLK = 1, STL = 1, AST = 1, REB = 1, FGM = 1, FTM = 1, FGA = -1, FTA = -1, TOV = -1):
    games_num = len(player['stats'])

    if game_number == -1:
        return compute_fantasy(player, games_num,
                        PTS, BLK, STL, AST, REB, FGM, FTM, FGA, FTA, TOV)

    elif game_number > games_num:
        print "This game does not exist, returned last game played instead"
        return compute_fantasy(player, games_num,
                        PTS, BLK, STL, AST, REB, FGM, FTM, FGA, FTA, TOV)

    else:
        game = player['stats'][game_number - 1]
        score = PTS*game[22] + BLK*game[19] + STL*game[18] + AST*game[17] + REB*game[16] + FGM*game[5]
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
            next_points = compute_fantasy(player, i + 1)
            curr_points = compute_fantasy(player, i)
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

#Computes fantasy score of a given game
def get_fantasy(game, PTS = 1, BLK = 1, STL = 1, AST = 1, REB = 1, FGM = 1, FTM = 1, FGA = -1, FTA = -1, TOV = -1):
    return PTS*game[22] + BLK*game[19] + STL*game[18] + AST*game[17] + REB*game[16] + FGM*game[5] \
           + FTM*game[11] + FGA*game[6] + FTA*game[12] + TOV*game[20]

#print compute_fantasy('2011-12', '977', 0)
# positions = []
# for file in os.listdir("data/2006-07/player_stats"):
#     player = pickle.load(open("data/2006-07/player_stats/" + file, 'rb'))
#     position = player['position']
#
#     if position not in positions:
#         positions.append(position)
#
# print positions
# #print average('2005-06', '15')[0]

#player = pickle.load(open('data' + os.sep + 'sample_' + os.sep + 'player_stats' + os.sep + '708' + '.pkl', 'rb'))
#print player['stats']
#print len(player['stats'])
#print average('sample_', player, 47, -2)[0]


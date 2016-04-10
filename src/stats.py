import pickle
import os

#This file takes "raw" data as input and computes additionnal stats such as averaged stats, winrate, fatansy points etc.

#Returns the averaged stats (all, home and away) of a given player in his first given number of games as well as winrate
#Returns averaged of all games but last by default
def average(season, playerID, number_games = -1):
    player = pickle.load(open('data' + os.sep + season + os.sep + 'player_stats' + os.sep + playerID + '.pkl', 'rb'))
    games_num = len(player['stats'])

    if number_games == 0:
        tmp = [0.]*23
        tmp[21] = player['experience']
        tmp[22] = player['age']
        return tmp, tmp, tmp
        # print "Please choose a strictly positive number of games"
        # exit()

    if number_games == -1:
        return average(season, playerID, games_num - 1)

    elif number_games > games_num:
        print "not enough games, returned average of all available games (%d)" % games_num
        return average(season, playerID, games_num)

    else:
        averaged = [float(sum(x))/float(len(x)) for x in zip(*[match[4:] for match in player['stats'][:number_games]])]
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
            home_won = float([match[3] for match in home].count('W'))
            home_winrate = home_won/len(home)
            home_avg.append(home_winrate)
            home_avg.append(player['experience'])
            home_avg.append(player['age'])

        if len(away) != 0:
            away_avg = [float(sum(x))/float(len(x)) for x in zip(*[match[4:] for match in away])]
            away_won = float([match[3] for match in away].count('W'))
            away_winrate = away_won/len(away)
            away_avg.append(away_winrate)
            away_avg.append(player['experience'])
            away_avg.append(player['age'])

        return averaged, home_avg, away_avg

#print average('2011-12', '201149')

#computes fantasy points of a given player on his given ith game (last by default)
#Allows different way of computing points but has espn values by default
def compute_fantasy(season, playerID, game_number = -1,
                    PTS = 1, BLK = 1, STL = 1, AST = 1, REB = 1, FGM = 1, FTM = 1, FGA = -1, FTA = -1, TOV = -1):
    player = pickle.load(open('data' + os.sep + season + os.sep + 'player_stats' + os.sep + playerID + '.pkl', 'rb'))
    games_num = len(player['stats'])

    if game_number == -1:
        return compute_fantasy(season, playerID, games_num,
                        PTS, BLK, STL, AST, REB, FGM, FTM, FGA, FTA, TOV)

    elif game_number > games_num:
        print "This game does not exist, returned last game played instead"
        return compute_fantasy(season, playerID, games_num,
                        PTS, BLK, STL, AST, REB, FGM, FTM, FGA, FTA, TOV)

    else:
        game = player['stats'][game_number - 1]
        score = PTS*game[20] + BLK*game[19] + STL*game[18] + AST*game[17] + REB*game[16] + FGM*game[5]
        + FTM*game[11] + FGA*game[6] + FTA*game[12] + TOV*game[20]

        return score

#returns weighted average with avg1 more important than avg by factor of weight
def weighted_average(avg1, avg2, weight):
    avg = []
    for a, b, in zip(avg1, avg2):
        tmp = (a + weight*b)/(weight + 1)
        avg.append(tmp)

    return avg

#compute_fantasy('2011-12', '977', 0)
#player = pickle.load(open('data' + os.sep + '2006-07' + os.sep + 'player_stats' + os.sep + '101144' + '.pkl', 'rb'))
#print player['stats'][0][2][4]
# print player['experience']
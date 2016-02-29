import pickle
import os

#This file takes "raw" data as input and computes additionnal stats such as averaged stats or Winrate

#Returns the averaged stats of a given player in his first given number of games
def average(season, playerID, number_games = -1):
    player = pickle.load(open('data' + os.sep + season + os.sep + 'player_stats' + os.sep + playerID + '.pkl', 'rb'))
    games_num = len(player['stats'])

    if number_games == -1:
        average(season, playerID, games_num)

    elif number_games > len(player['stats']):
        print "not enough games, returned average of all available games (%d)" % games_num
        average(season, playerID, games_num)

    else:
        return [float(sum(x))/float(len(x)) for x in zip(*[match[4:-1] for match in player['stats'][:number_games]])]

print average('2011-12', '255')
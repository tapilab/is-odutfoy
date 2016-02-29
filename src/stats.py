import pickle
import os

#This file takes "raw" data as input and computes additionnal stats such as averaged stats or Winrate

#Returns the averaged stats (all, home and away) of a given player in his first given number of games as well as winrate
def average(season, playerID, number_games = -1):
    player = pickle.load(open('data' + os.sep + season + os.sep + 'player_stats' + os.sep + playerID + '.pkl', 'rb'))
    games_num = len(player['stats'])

    if number_games == -1:
        average(season, playerID, games_num)

    elif number_games > len(player['stats']):
        print "not enough games, returned average of all available games (%d)" % games_num
        average(season, playerID, games_num)

    else:
        averaged = [float(sum(x))/float(len(x)) for x in zip(*[match[4:-1] for match in player['stats'][:number_games]])]
        won = float([match[3] for match in player['stats'][:number_games]].count('W'))
        winrate = won/number_games

        home = [match for match in player['stats'][:number_games] if match[2][4] == '@']
        home_avg = [float(sum(x))/float(len(x)) for x in zip(*[match[4:-1] for match in home])]
        home_won = float([match[3] for match in home].count('W'))
        home_winrate = home_won/len(home)

        away = [match for match in player['stats'][:number_games] if match[2][4] != '@']
        away_avg = [float(sum(x))/float(len(x)) for x in zip(*[match[4:-1] for match in away])]
        away_won = float([match[3] for match in away].count('W'))
        away_winrate = away_won/len(away)

        print (averaged, winrate), (home_avg, home_winrate), (away_avg, away_winrate)
        return (averaged, winrate), (home_avg, home_winrate), (away_avg, away_winrate)

print average('2011-12', '255')
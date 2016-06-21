import pickle
import os
import glob

#This file contains fucntions concerning experts opinion retrieval

months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

#Input a month in following format 'FEB', return month number (-1)
def month_to_number(month):
    return months.index(month)

#compares 2 dates given in following format : "FEB 10, 2015"
#returns true if date1 is before or equal date2
def date_before(date1, date2):
    year1, month1, day1 = int(date1[8:]), month_to_number(date1[:3]), int(date1[4:6])
    year2, month2, day2 = int(date2[8:]), month_to_number(date2[:3]), int(date2[4:6])

    if year1 < year2:
        return True

    elif year1 > year2:
        return False

    else:
        if month1 < month2:
            return True

        elif month1 > month2:
            return False

        else:
            return day1 <= day2

#returns true if date is in between start and end
def date_in(date, start, end):
    return date_before(date, end) and date_before(start, date)


#Returns the stats of a player between a start and end date in a given season
#date must follow following format : "FEB 10, 2015"
def get_games(season, playerID, start, end):
    player = pickle.load(open('data' + os.sep + season + os.sep + 'player_stats' + os.sep + playerID + '.pkl', 'rb'))
    print player['name']
    tmp = []
    for game in player['stats']:
        if date_in(game[1], start, end):
            tmp.append(game)

    return tmp

#print get_games("sample_", "708", "DEC 01, 2014", "MAR 01, 2015")

#Returns the stats of all players between start and end date in a given season
#date must follow following format : "FEB 10, 2015"
def get_all_games(season, start, end):
    players = glob.glob('data' + os.sep + season + os.sep + 'player_stats' + os.sep + "*.pkl")
    tmp = []

    for file in players:
        playerID = file[26:-4]
        games = get_games(season, playerID, start, end)
        tmp += games

    return tmp

#print get_all_games("sample_", "DEC 01, 2014", "MAR 01, 2015")

#Returns ID of a player given his name
def get_ID(season, name):
    players = glob.glob('data' + os.sep + season + os.sep + 'player_stats' + os.sep + "*.pkl")
    for file in players:
        playerID = file[26:-4]
        player = pickle.load(open('data' + os.sep + season + os.sep + 'player_stats' + os.sep + playerID + '.pkl', 'rb'))
        if player['name'] == name:
            return playerID

    print "Player could not be found"

print get_ID('2012-13', 'Jeremy Lin')

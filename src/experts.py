import pickle
import os
import glob
#from stats import *
import operator

#This file contains functions concerning experts opinion retrieval

months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
#months_31 = ['JAN', 'MAR', 'MAY', 'JUL', 'AUG', 'OCT'] #without december
months_30 = [4, 6, 9, 11]

#Input a month in following format 'FEB', return month number
def month_to_number(month):
    return months.index(month) + 1

#Inputs a number and returns the month in format 'FEB'
def number_to_month(number):
    if number <= 0 or number > 12:
        exit('This is not a month number')

    else:
        return months[number - 1]

#Outputs date with correct string format when day, month and year are given as numbers
def date_to_string(year, month, day):
    day = '0' + str(day) if day < 10 else str(day)
    return number_to_month(month) + ' ' + day + ', ' + str(year)

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

def is_leap_year(year):
    return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0

#adds days to date
def date_add(date, days):
    year, month, day = int(date[8:]), month_to_number(date[:3]), int(date[4:6])

    def date_update(day, month, year, month_lenght):
        if day + days <= month_lenght:
            day += days

        else:
            if month == 12:
                month = 1
                year += 1

            else:
                month += 1

            day += days - month_lenght

        return year, month, day

    if month == 2:
        if is_leap_year(year):
            year, month, day = date_update(day, month, year, 29)

        else:
            year, month, day = date_update(day, month, year, 28)

    elif month in months_30:
        year, month, day = date_update(day, month, year, 30)

    else:
        year, month, day = date_update(day, month, year, 31)

    return date_to_string(year, month, day)

#Returns the stats of a player between a start and end date in a given season
#date must follow following format : "FEB 10, 2015"
def get_games(player, start, end):
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
        player = pickle.load(open('data' + os.sep + season + os.sep + 'player_stats' + os.sep + playerID + '.pkl', 'rb'))
        games = get_games(player, start, end)
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

#print get_ID('2012-13', 'Jeremy Lin')

#Computes fantasy score of a given game
def get_fantasy(game, PTS = 1, BLK = 1, STL = 1, AST = 1, REB = 1, FGM = 1, FTM = 1, FGA = -1, FTA = -1, TOV = -1):
    return PTS*game[22] + BLK*game[19] + STL*game[18] + AST*game[17] + REB*game[16] + FGM*game[5] \
           + FTM*game[11] + FGA*game[6] + FTA*game[12] + TOV*game[20]

#Computes fantasy points in a given timestamp and returns most proficient players
def get_fantasies(season, start, end):
    players = glob.glob('data' + os.sep + season + os.sep + 'player_stats' + os.sep + "*.pkl")
    D = dict()

    for file in players:
        playerID = file[26:-4]
        player = pickle.load(open('data' + os.sep + season + os.sep + 'player_stats' + os.sep + playerID + '.pkl', 'rb'))
        games = get_games(player, start, end)
        score = 0

        if games != []:
            for game in games:
                score += get_fantasy(game)

            D[playerID] = score

    return sorted(D.items(), key=operator.itemgetter(1), reverse = True)

#given two dates and a player, returns the game numbers of first and last game played
def get_games_num(playerID, season, start, end):
    player = pickle.load(open('data' + os.sep + season + os.sep + 'player_stats' + os.sep + playerID + '.pkl', 'rb'))

    for i, game in enumerate(player['stats']):
        if date_in(game[1], start, end):
            first = i
            break

    last = len(player['stats']) - 1

    #in case no games are played in that period of time
    try:
        for j, game in enumerate(player['stats'][first:]):
            if not date_in(game[1], start, end):
                last = j + first - 1
                break

    except UnboundLocalError:
        return (-1, -1)

    return first, last


#test = get_fantasies('2014-15', 'OCT 20, 2014', 'DEC 15, 2014')
#print test
# print len(test)

#print get_ID('2012-13', 'Jeremy Lin')
# player = pickle.load(open('data' + os.sep + '2014-15' + os.sep + 'player_stats' + os.sep + '203953' + '.pkl', 'rb'))
# print player['stats']
# print get_games_num('203953', '2014-15', 'DEC 09, 2014', 'DEC 15, 2014')
#games = get_games(player, 'NOV 12, 2012', 'NOV 19, 2012')
# print games

#print date_add('FEB 25, 2016', 7)
#file containing obsolete code
"""

#creates a file having ID of a player as a name and containing only the name of the player
#player_list file mus exist for the given season
def get_names(season):
    player_list = pickle.load(open('data' + os.sep + season + os.sep + 'player_list.pkl', 'rb'))

    for i, player in enumerate(player_list['resultSets'][0]['rowSet']):

        req = requests.request('GET', 'http://stats.nba.com/stats/commonplayerinfo?LeagueID=00&PlayerID=' + str(player[0]) + '&SeasonType=Regular+Season', headers=headers, cookies=cookies)

        print "fetching name of player %d" % (i + 1)
        f = open('data' + os.sep + season + os.sep + 'player_names' + os.sep + str(player[0]) + '.txt', 'w')
        f.write(json.loads(req.content)['resultSets'][0]['rowSet'][0][3])
        f.close()


#get stats from all matches of a given player in a season (parameters must be strings)
#player_list must exist for given season
def get_stats(season, playerID):
    req = requests.request('GET', 'http://stats.nba.com/stats/playergamelog?LeagueID=00&PlayerID=' + playerID + '&Season=' + season + '&SeasonType=Regular+Season', headers=headers, cookies=cookies)

    pickle.dump(json.loads(req.content)['resultSets'][0]['rowSet'], open('data' + os.sep + season + os.sep + 'player_stats' + os.sep + playerID + '.pkl', 'wb'))

"""
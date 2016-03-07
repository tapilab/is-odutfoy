#This program fetches data of a season given as argument (use following format 2012-13 for example)

#import curl
#import urllib2
import requests
import json
import pickle
import os
from time import sleep
import sys
import shutil

#player_list = curl('http://stats.nba.com/stats/leaguedashplayerstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season=2013-14&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight=' -H 'Accept-Encoding: gzip, deflate, sdch' -H 'Accept-Language: en-US,en;q=0.8' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/45.0.2454.85 Chrome/45.0.2454.85 Safari/537.36' -H 'Accept: application/json, text/plain, */*' -H 'Referer: http://stats.nba.com/league/player/' -H 'Cookie: ug=564bc5cb06dd690a3c852e7da205ef8b; ugs=1; _gat=1; _ga=GA1.2.1028222052.1454632808; crtg_trnr=; s_cc=true; s_vi=[CS]v1|2B1C901605010772-40000146E0028408[CE]; s_sq=nbag-n-league%3D%2526pid%253Dstats.nba.com%25253A%25252Fplayer%25252F%2526pidt%253D1%2526oid%253Dhttp%25253A%25252F%25252Fstats.nba.com%25252Fplayer%25252F%2526ot%253DA; s_fid=611F6CAB17F03E6A-0F7BD99682C4658E' -H 'Connection: keep-alive' -H 'Cache-Control: max-age=0' --compressed)

cookies = {
    'ug': '564bc5cb06dd690a3c852e7da205ef8b',
    'ugs': '1',
    '_gat': '1',
    '_ga': 'GA1.2.1028222052.1454632808',
    'crtg_trnr': '',
    's_cc': 'true',
    's_vi': '[CS]v1|2B1C901605010772-40000146E0028408[CE]',
    's_sq': 'nbag-n-league%3D%2526pid%253Dstats.nba.com%25253A%25252Fplayer%25252F%2526pidt%253D1%2526oid%253Dhttp%25253A%25252F%25252Fstats.nba.com%25252Fplayer%25252F%2526ot%253DA',
    's_fid': '611F6CAB17F03E6A-0F7BD99682C4658E',
}

headers = {
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/45.0.2454.85 Chrome/45.0.2454.85 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'http://stats.nba.com/league/player/',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
}

#dumps in pickle file the list of players in a given season (has to be str i.e '2013-14')
def get_player_list(season):
    if os.path.exists('data' + os.sep + season):
        shutil.rmtree('data' + os.sep + season)

    os.makedirs('data' + os.sep + season)

    req = requests.request('GET', 'http://stats.nba.com/stats/leaguedashplayerstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season=' + season + '&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight=', headers=headers, cookies=cookies)

    player_list = json.loads(req.content)

    pickle.dump(player_list, open('data' + os.sep + season + os.sep + 'player_list.pkl', 'wb'))


#gets the data of all players for one season in a structured dict (player list of season must exist)
#season directory must exist
def get_data(season):
    if os.path.exists('data' + os.sep + season + os.sep + 'player_stats'):
        shutil.rmtree('data' + os.sep + season + os.sep + 'player_stats')

    os.makedirs('data' + os.sep + season + os.sep + 'player_stats')


    player_info = dict()

    player_list = pickle.load(open('data' + os.sep + season + os.sep + 'player_list.pkl', 'rb'))

    for i, player in enumerate(player_list['resultSets'][0]['rowSet']):

        print "fetching stats of player %d" % (i + 1)

        name_req = requests.request('GET', 'http://stats.nba.com/stats/commonplayerinfo?LeagueID=00&PlayerID=' + str(player[0]) + '&SeasonType=Regular+Season', headers=headers, cookies=cookies)
        sleep(1)

        player_info['name'] = json.loads(name_req.content)['resultSets'][0]['rowSet'][0][3]

        birthdate = json.loads(name_req.content)['resultSets'][0]['rowSet'][0][6]
        start_year = json.loads(name_req.content)['resultSets'][0]['rowSet'][0][22]

        player_info['experience'] = int(season.split('-')[0]) - start_year
        player_info['age'] = int(season.split('-')[0]) - int(birthdate.split('-')[0]) #approximation

        #may be interesting but incomplete for previous seasons
        # player_info['height'] = json.loads(name_req.content)['resultSets'][0]['rowSet'][0][10]
        # player_info['weight'] = json.loads(name_req.content)['resultSets'][0]['rowSet'][0][11]
        # player_info['position'] = json.loads(name_req.content)['resultSets'][0]['rowSet'][0][14]

        stats_req = requests.request('GET', 'http://stats.nba.com/stats/playergamelog?LeagueID=00&PlayerID=' + str(player[0]) + '&Season=' + season + '&SeasonType=Regular+Season', headers=headers, cookies=cookies)
        sleep(1)


        player_info['stats'] = []

        #removing useless data
        for match in json.loads(stats_req.content)['resultSets'][0]['rowSet']:
            player_info['stats'].append(match[2:-1])

        pickle.dump(player_info, open('data' + os.sep + season + os.sep + 'player_stats' + os.sep + str(player[0]) + '.pkl', 'wb'))

if len(sys.argv) < 2:
    print "Please input season you wish to retrieve data from as first argument"
    print "Season must be of following format xxxx-yy i.e : 2013-14"

else:
    get_player_list(sys.argv[1])
    get_data(sys.argv[1])

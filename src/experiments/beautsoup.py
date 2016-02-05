from bs4 import BeautifulSoup
import urllib2

page = urllib2.urlopen("http://stats.nba.com/player/#!/202710/gamelogs/").read()
soup = BeautifulSoup(page, "html5lib")

#for link in soup.find_all('a'):
#    print(link.get('href'))

#print soup.prettify()

print soup.find_all('a')
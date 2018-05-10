from unidecode import unidecode
from bs4 import BeautifulSoup
from csv import reader
import sys
import requests
from Modules.FBClasses import Player, get_hitter_positions
#import Modules.FBClasses

team = sys.argv[1]
position = sys.argv[2]

def get_yahoo_players(team: str, position: str):
    is_hitter = bool(position in get_hitter_positions())
    yahoo_players = []

    first_url = "https://baseball.fantasysports.yahoo.com/b1/5983/\
players?&sort=OR&sdir=1&status="
    first_url += str(team)
    first_url += "&pos="
    first_url += position
    first_url += "&stat1=S_S_2016&jsenabled=1"

    subsequent_url = "https://baseball.fantasysports.yahoo.com/b1/5983/\
players?status=A&pos="
    subsequent_url += position
    subsequent_url += "&cut_type=33&stat1=S_S_2017&myteam=0&\
sort=OR&sdir=1&count=" 
    #        sys.stdout.write('\n')

    r = requests.get(first_url)
    line = unidecode(r.text)
    soup = BeautifulSoup(line, 'lxml')
    for s in soup.find_all('a'):
        try:
            if 'name' in s['class']:
                player = Player(name=str(s.string).strip(), \
                    hitter=is_hitter, \
                    positions=[position])
                #yahoo_players.append(str(s.string))
                yahoo_players.append(player)
        except:
            continue
    if team == 'A':
        for count in range(25, 225, 25):
            url = subsequent_url + str(count)
            try:
                r = requests.get(url)
                line = unidecode(r.text)
                soup = BeautifulSoup(line, 'lxml')
                for s in soup.find_all('a'):
                    try:
                        if 'name' in s['class']:
                            #yahoo_players.append(str(s.string))
                            player = Player(name=str(s.string).strip(), \
                                hitter = is_hitter, \
                                positions=[position])
                            yahoo_players.append(player)
                    except:
                        continue
            except:
                break

    #yahoo_players = [p.strip() for p in yahoo_players]
    return yahoo_players

def get_razzball_players():
    razzball_players = []

    with open('razzball.csv', 'r') as razz_csv:
        r = reader(razz_csv)
        next(r)
        for line in r:
            pos = line[3].split('/')
            is_hitter = not any([p for p in pos if 'p' in p.lower()])
            player = Player(name = line[1].strip(), team = line[2], \
                            hitter = is_hitter, \
                            positions = pos, \
                            value = float(line[4]))
            razzball_players.append(player)
    return razzball_players

def get_players_with_values(team: str, position: str):
    yahoo_players = get_yahoo_players(team, position)
    razzball_players = get_razzball_players()
    razzball_players = [r for r in razzball_players if r.name.lower() \
                        in [p.name.lower() for p in yahoo_players]]
    if position == "B":
        razzball_players = [r for r in razzball_players \
                            if r.hitter]
    elif position == "P":
        razzball_players = [r for r in razzball_players \
                            if not r.hitter]
    else:
        razzball_players = [r for r in razzball_players \
                            if position in r.positions]
    razzball_players.sort(key = lambda p: p.value, reverse = True)
    return razzball_players

razzball_players = get_players_with_values(sys.argv[1], sys.argv[2])
if sys.argv[3] == "sum":
    sys.stdout.write(str(sum([max(0, p.value) for p in razzball_players])))
    sys.stdout.write('\n')
elif sys.argv[3] == "max":
    sys.stdout.write(str(max([p.value for p in razzball_players])))
    sys.stdout.write('\n')
elif sys.argv[3] == "min":
    sys.stdout.write(str(min([p.value for p in razzball_players])))
    sys.stdout.write('\n')
else:
    for p in razzball_players:
        sys.stdout.write(p.name.ljust(25))
        sys.stdout.write(p.team.ljust(5))
        sys.stdout.write('/'.join(p.positions).ljust(10))
        sys.stdout.write(str(p.value).ljust(10))
        sys.stdout.write('\n')


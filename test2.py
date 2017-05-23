from bs4 import BeautifulSoup
import requests

def get_razzball_players():
    url = "http://razzball.com/playerrater-preseason-yahoomlb12/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    soup = soup.find_all('tbody')[1]
    players = []
    name = None
    team = None
    pos = None
    val = None
    for s in soup.find_all('td'):
        if any(s.findChildren()):
            child = s.findChildren()[0]
            if not name:
                for att in child.attrs:
                    if att == 'href' and 'player' in child[att]:
                        name = str(s.findChildren()[0].string)
                        continue
            else:
                for att in child.attrs:
                    if att == 'href' and 'team' in child[att]:
                        team = str(s.findChildren()[0].string)
                        continue
        elif name and team and not pos:
            try:
                pos = str(s.string)
            except:
                continue
        elif name and team and pos and str(s.string).strip():
            try:
                val = float(s.string)
            except:
                continue
            else:
                players.append({'name': name, 'team': team, \
                                'pos': pos, 'val': val})
                name = None
                val = None
    return players


for player in get_razzball_players():
    values = [player['name'], player['team'], player['pos'], player['val']]
    values = ['"'+str(s)+'"' for s in values]
    print(','.join(values))

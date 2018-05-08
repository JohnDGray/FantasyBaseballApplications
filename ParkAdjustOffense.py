from csv import reader
from unidecode import unidecode
from bs4 import BeautifulSoup
import requests
import numpy

team_names = (
    'ari',
    'atl',
    'bal',
    'bos',
    'chc',
    'chw',
    'cin',
    'cle',
    'col',
    'det',
    'flo',
    'hou',
    'kan',
    'laa',
    'lad',
    'mil',
    'min',
    'nym',
    'nyy',
    'oak',
    'phi',
    'pit',
    'sd',
    'sea',
    'sfg',
    'stl',
    'tb',
    'tex',
    'tor',
    'wsh'
)

fangraphs_team_names = {
    'diamondbacks': team_names[0],
    'braves': team_names[1],
    'orioles': team_names[2],
    'red sox': team_names[3],
    'cubs': team_names[4],
    'white sox': team_names[5],
    'reds': team_names[6],
    'indians': team_names[7],
    'rockies': team_names[8],
    'tigers': team_names[9],
    'marlins': team_names[10],
    'astros': team_names[11],
    'royals': team_names[12],
    'angels': team_names[13],
    'dodgers': team_names[14],
    'brewers': team_names[15],
    'twins': team_names[16],
    'mets': team_names[17],
    'yankees': team_names[18],
    'athletics': team_names[19],
    'phillies': team_names[20],
    'pirates': team_names[21],
    'padres': team_names[22],
    'mariners': team_names[23],
    'giants': team_names[24],
    'cardinals': team_names[25],
    'rays': team_names[26],
    'rangers': team_names[27],
    'blue jays': team_names[28],
    'nationals': team_names[29]
}

class TeamWithRpgAndParkFactor(object):

    """Docstring for TeamWithRpgAndParkFactor. """

    def __init__(self, team_name, rpg, park_factor):
        """TODO: to be defined1. """
        self.team_name = team_name
        self._park_factor = park_factor
        self._neutral_rpg = 2 * rpg / (1 + park_factor)

    def get_adjusted_rpg(self, park_factor):
        return self._neutral_rpg * park_factor

def get_runs_per_game_all():
    url = "https://www.fangraphs.com/depthcharts.aspx?position=Standings"
    request_result = requests.get(url)
    line = unidecode(request_result.text)
    soup = BeautifulSoup(line, 'lxml')
    rows = soup.find('form').find('div', id='wrapper')\
           .find('div', id='content').find_all('div')[3].find('table').find_all('tr')
    teams_with_vals = []
    for row in rows[2:32]:
        cells = row.find_all('td')
        team_name = fangraphs_team_names[cells[0].text.lower()]
        rpg = float(cells[13].text)
        teams_with_vals.append((team_name, rpg))
    return teams_with_vals

def get_park_factors():
    teams_with_park_factors = []
    with open('ParkFactors2018.csv', 'r') as park_factors:
        csv = reader(park_factors)
        for row in csv:
            team_name = row[0]
            park_factor = float(row[10])
            teams_with_park_factors.append((team_name, park_factor))
    return teams_with_park_factors

def get_team(team_name, teams_with_rpg, teams_with_park_factors):
    team_name = team_name.lower()
    team_with_rpg = next(iter([t for t in teams_with_rpg if t[0] == team_name]), None)
    team_park = next(iter([t for t in teams_with_park_factors if t[0] == team_name]), None)
    if not team_with_rpg or not team_park:
        raise Exception("Invalid team name")
    team = TeamWithRpgAndParkFactor(team_name, team_with_rpg[1], team_park[1])
    return team

def get_avg_stedev(rpg_vals):
    arr = numpy.array(rpg_vals)
    avg = numpy.mean(arr, axis=0)
    stdev = numpy.std(arr, axis=0)
    return (avg, stdev)

def get_stdevs_above_avg(val, avg, stdev):
    return (val-avg)/stdev

def get_multiple_adjusted_rpg(teams_with_parks):
    teams_with_rpg = get_runs_per_game_all()
    teams_with_park_factors = get_park_factors()
    avg, stdev = get_avg_stedev([t[1] for t in teams_with_rpg])
    results = []
    for t in teams_with_parks:
        team_name = t[0]
        park_team_name = t[1]
        team = get_team(team_name, teams_with_rpg, teams_with_park_factors)
        park_factor = [v[1] for v in teams_with_park_factors if v[0] == park_team_name][0]
        print("offense:", team_name)
        print("park:", park_team_name)
        adjusted_rpg = team.get_adjusted_rpg(park_factor)
        print("stdevs above avg:", get_stdevs_above_avg(adjusted_rpg, avg, stdev))
        print()

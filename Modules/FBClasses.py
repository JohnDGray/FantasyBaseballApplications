import collections
import itertools
import csv
import unidecode
import re

#assumed values
all_positions = frozenset(["c", "1b", "2b", "3b", "ss", "of", "util", "sp", "rp"])

yahoo_name_column=0
yahoo_dollar_column=2

yahoo_path = "/home/myname/Documents/Yahoo.csv"
steamer_hitter_path='/home/myname/Documents/SteamerHitters.csv'
steamer_pitcher_path='/home/myname/Documents/SteamerPitchers.csv'

steamer_hitter_value_indices = {
    'name':1,
    'team': 2,
    'position':5
}

steamer_hitter_statistic_indices = {
        'g':6,
        'pa':7,
        'ab':8,
        'r':9,
        'hr':10,
        'rbi':11,
        'sb':12,
        'h':13,
        'avg':24
}

steamer_pitcher_value_indices = {
    'name':1,
    'team': 2,
    'position':3
}

steamer_pitcher_statistic_indices = {
        'g':5,
        'gs':6,
        'ip':9,
        'w':10,
        'sv':12,
        'hld':13,
        'era':14,
        'whip':16,
        'k':17
}

steamer_position_delimiter = '/'

#code

Player = collections.namedtuple('Player', 'name team positions statistics value')

def clean_str(s):
    return s.strip().lower()

def player_has_pos(player, position):
    return position in player.positions

def is_hitter(player):
    hitter_positions = frozenset(['c', '1b', '2b', '3b', 'ss', 'of', 'util'])
    return frozenset(player.positions) & hitter_positions

def is_pitcher(player):
    pitcher_positions = frozenset(['sp', 'rp'])
    return frozenset(player.positions) & pitcher_positions

def count_by_pos(players_by_position):
    return {pos: len(players) for pos, players in players_by_position.items()}

def total_value_by_pos(players_by_position):
    results = {}
    for pos in players_by_position:
        total_value = sum(max(0, p.value) for p in players_by_position[pos])
        results[pos] = total_value
    return results

def group_by_position(players, position_substitutions):
    position_player_dict = collections.defaultdict(list)
    pitcher_cycle = itertools.cycle(["sp", "rp"])
    position_count = {pos:0 for pos in all_positions}
    for p in players:
        position_to_assign = None
        player_positions = set(p.positions)
        if "c" in player_positions:
            position_to_assign = "c"
        elif "2b" in player_positions and "ss" in player_positions:
            if position_count["2b"] <= position_count["ss"]:
                position_to_assign = "2b"
            else:
                position_to_assign = "ss"
        elif "2b" in player_positions:
            position_to_assign = "2b"
        elif "ss" in player_positions:
            position_to_assign = "ss"
        elif "3b" in player_positions:
            position_to_assign = "3b"
        elif "1b" in player_positions and "of" in player_positions:
            if 2*position_count["1b"] < position_count["of"]:
                position_to_assign = "1b"
            else:
                position_to_assign = "of"
        elif "1b" in player_positions:
            position_to_assign = "1b"
        elif "of" in player_positions:
            position_to_assign = "of"
        elif "sp" in player_positions and "rp" in player_positions:
            position_to_assign = next(pitcher_cycle)
        elif "sp" in player_positions:
            position_to_assign = "sp"
        elif "rp" in player_positions:
            position_to_assign = "rp"
        else:
            position_to_assign = "util"
        if position_to_assign in position_substitutions:
            position_to_assign = position_substitutions[position_to_assign]
        position_player_dict[position_to_assign].append(p)
        position_count[position_to_assign] += 1
    return position_player_dict
def get_yahoo_players():
    yahoo_players = []
    with open(yahoo_path, 'r') as yahoo:
        r = csv.reader(yahoo)
        for line in r:
            nm = unidecode.unidecode(line[yahoo_name_column])
            m = re.search('(.*)(day\-to\-day)\s*', nm, re.IGNORECASE)
            if m:
                nm = m.group(1)
            m = re.search('(.*)(\s*not\s+active)\s*', nm, re.IGNORECASE)
            if m:
                nm = m.group(1)
            m = re.search('(.*player notes?\s+)(.*)', nm, re.IGNORECASE)
            nm = m.group(2)

            m = re.search('(.+)\s+(\w+)\s+\-([^\-]+)$', nm, re.IGNORECASE)
            nm = clean_str(m.group(1))
            tm = clean_str(m.group(2))

            pos = frozenset(clean_str(s) for s in m.group(3).split(','))

            # pos_with_util = m.group(3).split(',')
            # pos = []
            # for position in pos_with_util:
            #     s = clean_str(position)
            #     if s in position_substitutions:
            #         replacement_pos = position_substitutions[s]
            #         pos.append(replacement_pos)
            #     else:
            #         pos.append(s)
            # pos = frozenset(pos)

            vl = unidecode.unidecode(line[yahoo_dollar_column])
            m = re.search('(.*\$\s*)(.*)', vl, re.IGNORECASE)
            vl = float(m.group(2))

            player = Player(name=nm, team=tm, positions=pos, statistics=None, value=vl)
            yahoo_players.append(player)
    return yahoo_players

def get_steamer_projections(csv_path, attribute_indices, pos_delimiter, \
                            statistic_indices=None, skip_lines=1):
    players = []
    player_values = {}
    player_statistics = {}
    name_index = attribute_indices['name']
    team_index = attribute_indices['team']
    position_index = attribute_indices['position']
    value_index = 'value' in attribute_indices and \
                  attribute_indices['value']
    with open(csv_path, 'r') as csv_file:
        r = csv.reader(csv_file)
        for _ in range(skip_lines):
            next(r)
        for l in r:
            line = [unidecode.unidecode(x) for x in l]
            nm = clean_str(line[name_index])
            tm = clean_str(line[team_index])

            pos = frozenset(clean_str(s) for s in line[position_index].split(pos_delimiter))

            val = (value_index and float(line[value_index])) or None
            stats = {}
            if statistic_indices:
                for stat in statistic_indices:
                    stats[stat] = float(line[statistic_indices[stat]])
                if 'sv' in stats and 'hld' in stats:
                    stats['sv+hld'] = stats['sv'] + stats['hld']
                stats = tuple((k, v) for k, v in stats.items())
            stats = stats or None
            player = Player(nm, tm, pos, stats, val)
            players.append(player)

    return players

def get_steamer_hitters():
    return get_steamer_projections(steamer_hitter_path,
                                   steamer_hitter_value_indices, 
                                   steamer_position_delimiter, 
                                   steamer_hitter_statistic_indices, 
                                   skip_lines=1)

def get_steamer_pitchers():
    return get_steamer_projections(steamer_pitcher_path,
                                   steamer_pitcher_value_indices, 
                                   steamer_position_delimiter, 
                                   steamer_pitcher_statistic_indices, 
                                   skip_lines=1)

def get_steamer_players():
    return get_steamer_hitters() + get_steamer_pitchers()

def get_player_str(player):
    nm, tm = str(player.name), str(player.team)
    pos = '/'.join(list(player.positions))
    stats = player.statistics and str(list(player.statistics))
    value = player.value and str(int(round(player.value,0))) 
    return [x for x in [nm, tm, pos, stats, value] if x]


if __name__ == '__main__':
    y = get_yahoo_players()
    sh = get_steamer_hitters()
    sp = get_steamer_pitchers()

    for p in y:
        s = get_player_str(p)
        print(s)

    for p in sh:
        s = get_player_str(p)
        print(s)

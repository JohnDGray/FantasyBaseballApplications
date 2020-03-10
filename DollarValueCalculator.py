from collections import namedtuple
from csv import reader, writer
from unidecode import unidecode
from collections import defaultdict
import itertools
import re
import statistics

#assmued values:
write_output = True
steamer_hitter_path = "/home/myname/Downloads/SteamerHitters.csv"
steamer_pitcher_path = "/home/myname/Downloads/SteamerPitchers.csv"
yahoo_csv_path = "/home/myname/Downloads/Yahoo.csv"
output_path = "/home/myname/Downloads/FantasyValues.csv"

rate_stat_qualifiers = {
        'avg':'ab',
        'era':'ip',
        'whip':'ip'
}

stats_to_reverse = frozenset(['era', 'whip'])

num_to_draft=12*23
draft_dollars=12*260

all_positions = frozenset(["c", "1b", "2b", "3b", "ss", "of", "util", "sp", "rp"])

position_substitutions = {
        'dh': 'util',
        'of': 'util',
        '1b': 'util'
}

yahoo_name_column=0
yahoo_dollar_column=2

steamer_position_delimiter = '/'

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

#end assumed values

Player = namedtuple('Player', 'name team positions statistics value')
Stat_Results = namedtuple('Stat_Results', 'max min mean stdev')

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
    with open(csv_path, 'r') as csv:
        r = reader(csv)
        for _ in range(skip_lines):
            next(r)
        for l in r:
            line = [unidecode(x) for x in l]
            nm = clean_str(line[name_index])
            tm = clean_str(line[team_index])

            pos = frozenset(clean_str(s) for s in line[position_index].split(pos_delimiter))

            # pos_with_dh = line[position_index].split(pos_delimiter)
            # pos = []
            # for position in pos_with_dh:
            #     s = clean_str(position)
            #     if s in position_substitutions:
            #         replacement_pos = position_substitutions[s]
            #         pos.append(replacement_pos)
            #     else:
            #         pos.append(s)
            # pos = frozenset(pos)

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

def get_yahoo_players():
    yahoo_players = []
    with open(yahoo_csv_path, 'r') as yahoo:
        r = reader(yahoo)
        for line in r:
            nm = unidecode(line[yahoo_name_column])
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

            vl = unidecode(line[yahoo_dollar_column])
            m = re.search('(.*\$\s*)(.*)', vl, re.IGNORECASE)
            vl = float(m.group(2))

            player = Player(name=nm, team=tm, positions=pos, statistics=None, value=vl)
            yahoo_players.append(player)
    return yahoo_players


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

def group_by_position(players):
    position_player_dict = defaultdict(list)
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

def count_by_pos(players_by_position):
    return {pos: len(players) for pos, players in players_by_position.items()}

def total_value_by_pos(players_by_position):
    results = {}
    for pos in players_by_position:
        total_value = sum(max(0, p.value) for p in players_by_position[pos])
        results[pos] = total_value
    return results

def get_stat_results(values):
    mx = max(values)
    mn = min(values)
    mean = statistics.mean(values)
    stdev = statistics.pstdev(values)
    return Stat_Results(mx, mn, mean, stdev)

def get_z_scores(all_players, top_players, stat):
    def helper(pv, sr):
        zs = {}
        for p, v in pv.items():
            z = (v - sr.mean) / sr.stdev
            zs[p] = z
        return zs

    all_player_values = {p: dict(p.statistics)[stat] for p in all_players}
    top_player_values = {p: dict(p.statistics)[stat] for p in top_players}
    stat_results = get_stat_results(top_player_values.values())
    z_scores = helper(all_player_values, stat_results)
    if stat in stats_to_reverse:
        z_scores = {p: -1 * z for p, z in z_scores.items()}
    if stat in rate_stat_qualifiers:
        qualifier = rate_stat_qualifiers[stat]
        all_player_values = {p: dict(p.statistics)[qualifier] * z for p, z in z_scores.items()}
        top_player_values = {p: all_player_values[p] for p in top_player_values}
        stat_results = get_stat_results(top_player_values.values())
        z_scores = helper(all_player_values, stat_results)
    return z_scores

def get_player_values(all_players, top_players, hitter_stats, pitcher_stats):
    all_hitters = tuple(p for p in all_players if is_hitter(p))
    all_pitchers = tuple(p for p in all_players if is_pitcher(p))
    top_hitters = tuple(p for p in top_players if is_hitter(p))
    top_pitchers = tuple(p for p in top_players if is_pitcher(p))
    all_z_scores = defaultdict(list)
    for stat in hitter_stats:
        z_scores = get_z_scores(all_hitters, top_hitters, stat)
        for player, z in z_scores.items():
            all_z_scores[player].append(z)
    for stat in pitcher_stats:
        z_scores = get_z_scores(all_pitchers, top_pitchers, stat)
        for player, z in z_scores.items():
            all_z_scores[player].append(z)
    new_players = []
    for player, zs in all_z_scores.items():
        value = sum(z for z in zs)
        name, team, positions, statistics = player.name, player.team, \
                                            player.positions, player.statistics
        new_players.append(Player(name, team, positions, statistics, value))
    return frozenset(new_players)

def limit_by_counts(players, count_by_position):
    players_by_position = group_by_position(players)
    new_players = []
    for pos in count_by_position:
        n = count_by_position[pos]
        new_players += players_by_position[pos][:n]
    return new_players

def val_above_replacement(players, count_by_position):
    players_by_position = group_by_position(players)
    pos_replacement_val = {}
    for pos in count_by_position:
        n = count_by_position[pos]
        if n > 0:
            p = players_by_position[pos][n-1]
            pos_replacement_val[pos] = p.value
    new_players = []
    for pos, players in players_by_position.items():
        replacement_val = pos_replacement_val[pos]
        for p in players:
            new_value = p.value - replacement_val
            name, team, positions, statistics = p.name, p.team, p.positions, p.statistics
            new_player = Player(name, team, positions, statistics, new_value)
            new_players.append(new_player)
    return frozenset(new_players)

def get_dollar_values(players, dollars_by_position):
    new_players = []
    players_by_position = group_by_position(players)
    for pos, players in players_by_position.items():
        dollars = dollars_by_position[pos]
        total_value = sum(max(0, p.value) for p in players)
        for player in players:
            name = player.name
            team = player.team
            positions = player.positions
            statistics = player.statistics
            value = (player.value / total_value) * dollars
            new_player = Player(name, team, positions, statistics, value)
            new_players.append(new_player)
    return new_players

def recalculate_values(players_with_values, position_counts, hitter_stats, pitcher_stats):
    players_limited = limit_by_counts(players_with_values, position_counts)
    players_with_values = get_player_values(players_with_values, \
                                            players_limited, \
                                            hitter_stats, \
                                            pitcher_stats)
    return sorted(players_with_values, key=lambda p: p.value, reverse=True)

def recalculation_needed(old_players, new_players, acceptable_pct_ch):
    old_player_dict = {', '.join((p.name, p.team, str(p.positions))): p.value for p in old_players}
    new_player_dict = {', '.join((p.name, p.team, str(p.positions))): p.value for p in new_players}
    max_ch = 0
    max_player = None
    for name, val1 in old_player_dict.items():
        val2 = new_player_dict[name]
        diff = abs((val1 - val2))
        pct_ch = max(diff/val1, diff/val2)
        if pct_ch > max_ch:
            max_player = (name, val1, val2)
            max_ch = pct_ch
    return max_ch > acceptable_pct_ch

def get_statistic_total(players, stat):
    total = 0 
    for p in players:
        stats = dict(p.statistics)
        if stat in stats:
            value = stats[stat]
            total += value
    return total

def print_by_position(steamer_by_position, yahoo_by_position, *positions):
    for pos in positions:
        print(f"Steamer {pos}")
        for player in steamer_by_position[pos]:
            name = player.name
            value = player.value
            print(f"{name: <30} {value:.1f}")
        print()
        print(f"Yahoo {pos}")
        for player in yahoo_by_position[pos]:
            name = player.name
            value = player.value
            print(f"{name: <30} {value:.1f}")
        print()
        print()

def get_player_str(player):
    nm, tm = str(player.name), str(player.team)
    pos = '/'.join(list(player.positions))
    stats = str(list(player.statistics))
    value = str(int(round(player.value,0))) 
    return [nm, tm, pos, stats, value]


    
#main code

yahoo_players = get_yahoo_players()
steamer_hitters = get_steamer_projections(steamer_hitter_path, steamer_hitter_value_indices, \
                                          steamer_position_delimiter, \
                                          steamer_hitter_statistic_indices, True)

steamer_pitchers = get_steamer_projections(steamer_pitcher_path, steamer_pitcher_value_indices, \
                                           steamer_position_delimiter, \
                                           steamer_pitcher_statistic_indices, True)

steamer_players = steamer_hitters + steamer_pitchers
steamer_players = steamer_players[::-1]

yahoo_players = sorted(yahoo_players, key=lambda p: p.value, reverse=True)
yahoo_players = yahoo_players[:num_to_draft]
yahoo_total_value = sum(p.value for p in yahoo_players)
scalar = draft_dollars / yahoo_total_value
yahoo_players = list(Player(*p[:4], scalar * p.value) for p in yahoo_players)
yahoo_total_value = sum(p.value for p in yahoo_players)
yahoo_by_position = group_by_position(yahoo_players)
yahoo_position_counts = count_by_pos(yahoo_by_position)
yahoo_value_by_position = total_value_by_pos(yahoo_by_position)
                        

hitter_stats_to_use = ['r', 'hr', 'rbi', 'sb', 'avg']
pitcher_stats_to_use = ['w', 'sv+hld', 'k', 'era', 'whip']

acceptable_pct_ch = 0.000001
iteration = 1
steamer_with_values = recalculate_values(steamer_players, \
                                         yahoo_position_counts, \
                                         hitter_stats_to_use, \
                                         pitcher_stats_to_use)
recalc_needed = True
while recalc_needed:
    iteration += 1
    old_steamer_with_values = steamer_with_values
    steamer_with_values = recalculate_values(steamer_with_values, \
                                             yahoo_position_counts, \
                                             hitter_stats_to_use, \
                                             pitcher_stats_to_use)
    recalc_needed = recalculation_needed(old_steamer_with_values, steamer_with_values, \
                                         acceptable_pct_ch)

steamer_with_values = val_above_replacement(steamer_with_values, yahoo_position_counts)
steamer_with_values = sorted(steamer_with_values, key=lambda p: p.value, reverse=True)
steamer_limited = limit_by_counts(steamer_with_values, yahoo_position_counts)
steamer_with_values = get_dollar_values(steamer_limited, yahoo_value_by_position)
steamer_with_values = sorted(steamer_with_values, key=lambda p: p.value, reverse=True)
steamer_by_position = group_by_position(steamer_with_values)
steamer_value_by_position = total_value_by_pos(steamer_by_position)

if write_output and output_path:
    with open(output_path, 'w') as output:
        w = writer(output)
        for p in steamer_with_values:
            w.writerow(get_player_str(p))

import collections
import csv
import collections
import Modules.FBClasses as fb_classes
import itertools
import re
import statistics

#assmued values:
write_output = False
output_path = "/home/myname/Documents/FantasyValues.csv"

rate_stat_qualifiers = {
        'avg':'ab',
        'era':'ip',
        'whip':'ip'
}

stats_to_reverse = frozenset(['era', 'whip'])

num_to_draft=12*23
draft_dollars=12*260

position_substitutions = {
        'dh': 'util',
        'of': 'util',
        '1b': 'util'
}

#functions
Stat_Results = collections.namedtuple('Stat_Results', 'max min mean stdev')

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
    all_hitters = tuple(p for p in all_players if fb_classes.is_hitter(p))
    all_pitchers = tuple(p for p in all_players if fb_classes.is_pitcher(p))
    top_hitters = tuple(p for p in top_players if fb_classes.is_hitter(p))
    top_pitchers = tuple(p for p in top_players if fb_classes.is_pitcher(p))
    all_z_scores = collections.defaultdict(list)
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
        new_players.append(fb_classes.Player(name, team, positions, statistics, value))
    return frozenset(new_players)

def limit_by_counts(players, count_by_position):
    players_by_position = fb_classes.group_by_position(players, position_substitutions)
    new_players = []
    for pos in count_by_position:
        n = count_by_position[pos]
        new_players += players_by_position[pos][:n]
    return new_players

def val_above_replacement(players, count_by_position):
    players_by_position = fb_classes.group_by_position(players, position_substitutions)
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
            new_player = fb_classes.Player(name, team, positions, statistics, new_value)
            new_players.append(new_player)
    return frozenset(new_players)

def get_dollar_values(players, dollars_by_position):
    new_players = []
    players_by_position = fb_classes.group_by_position(players, position_substitutions)
    for pos, players in players_by_position.items():
        dollars = dollars_by_position[pos]
        total_value = sum(max(0, p.value) for p in players)
        for player in players:
            name = player.name
            team = player.team
            positions = player.positions
            statistics = player.statistics
            value = (player.value / total_value) * dollars
            new_player = fb_classes.Player(name, team, positions, statistics, value)
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


    
#main code
yahoo_players = fb_classes.get_yahoo_players()
steamer_players = fb_classes.get_steamer_players()[::-1]
# steamer_players = steamer_players[::-1]

yahoo_players = sorted(yahoo_players, key=lambda p: p.value, reverse=True)
yahoo_players = yahoo_players[:num_to_draft]
yahoo_total_value = sum(p.value for p in yahoo_players)
scalar = draft_dollars / yahoo_total_value
yahoo_players = list(fb_classes.Player(*p[:4], scalar * p.value) for p in yahoo_players)
yahoo_total_value = sum(p.value for p in yahoo_players)
yahoo_by_position = fb_classes.group_by_position(yahoo_players, position_substitutions)
yahoo_position_counts = fb_classes.count_by_pos(yahoo_by_position)
yahoo_value_by_position = fb_classes.total_value_by_pos(yahoo_by_position)
                        

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
steamer_by_position = fb_classes.group_by_position(steamer_with_values, position_substitutions)
steamer_value_by_position = fb_classes.total_value_by_pos(steamer_by_position)

if write_output and output_path:
    with open(output_path, 'w') as output:
        w = csv.writer(output)
        for p in steamer_with_values:
            w.writerow(fb_classes.get_player_str(p))
else:
    for p in steamer_with_values:
        print(fb_classes.get_player_str(p))

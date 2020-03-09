import typing
import statistics
import itertools
import functools
from collections import defaultdict
from unidecode import unidecode
from csv import reader
from enum import Enum


class Player_Attributes(Enum):
    NAME=1
    TEAM=2
    POSITION=3
    VALUE=4

class Position(Enum):
    HITTER=1
    PITCHER=2
    C=3
    FIRST_BASE=4
    SECOND_BASE=5
    THIRD_BASE=6
    SS=7
    OF=8
    UTIL=9
    SP=10
    RP=11

def get_position_from_str(pos):
    values = {
        'c':Position.C,
        '1b':Position.FIRST_BASE,
        '2b':Position.SECOND_BASE,
        '3b':Position.THIRD_BASE,
        'ss':Position.SS,
        'of':Position.OF,
        'util':Position.UTIL,
        'dh':Position.UTIL,
        'sp':Position.SP,
        'rp':Position.RP
    }
    return values[pos.strip().lower()]
    
class Statistic(Enum):
    G=1
    PA=2
    AB=3
    H=4
    R=5
    HR=6
    RBI=7
    SB=8
    AVG=9
    GS=10
    IP=11
    W=12
    SV=13
    K=14
    HLD=15
    SVHLD=16
    ER=17
    BB=18
    ERA=19
    WHIP=20

def get_statistic_from_str(stat):
    values = {
        'g':Statistic.G,
        'pa':Statistic.PA,
        'ab':Statistic.AB,
        'h':Statistic.H,
        'r':Statistic.R,
        'hr':Statistic.HR,
        'rbi':Statistic.RBI,
        'sb':Statistic.SB,
        'avg':Statistic.AVG,
        'gs':Statistic.GS,
        'ip':Statistic.IP,
        'w':Statistic.W,
        'sv':Statistic.SV,
        'k':Statistic.K,
        'hld':Statistic.HLD,
        'svhld':Statistic.SVHLD,
        'er':Statistic.ER,
        'bb':Statistic.BB,
        'era':Statistic.ERA,
        'whip':Statistic.WHIP
    }
    return values[stat.strip().lower()]

class Statistical_Calculation(Enum):
    MIN=1
    MAX=2
    MEAN=3
    STDEV=4

def stat_results(stats):
        results = {}
        for stat in stats:
            values = stats[stat]
            min_vl = min(values)
            max_vl = max(values)
            mean_vl = statistics.mean(values)
            stdev_vl = statistics.pstdev(values)
            results[stat] = {
                Statistical_Calculation.MIN:min_vl,
                Statistical_Calculation.MAX:max_vl,
                Statistical_Calculation.MEAN:mean_vl,
                Statistical_Calculation.STDEV:stdev_vl
            }
        return results
            
def collect_stats(players):
    all_stats = defaultdict(list)
    for p in players:
        stats = p.statistics
        for stat_name in stats:
            all_stats[stat_name].append(stats[stat_name])
    return all_stats


def has_pos(player, position):
    return position in player.positions

def has_all_pos(player, position_list):
    for position in position_list:
        if not position in player.positions:
            return False
    return True

def is_pitcher(player):
    pitcher_positions = [Position.SP, Position.RP]
    return any(pos for pos in pitcher_positions if has_pos(player, pos))

def is_hitter(player):
    return not is_pitcher(player)

def update_player_value(player, new_value):
    return Player(player.name, player.team, player.positions, player.statistics, new_value)

def update_player_values(players, func):
    for p in players:
        yield Player(p.name, p.team, p.positions, p.statistics, func(p.value))

@functools.total_ordering
class Player:
    def __init__(self, name, team, positions, statistics=None, value=None):
        self.name = str(name)
        self.team = str(team)
        self.positions = frozenset(positions)
        self.statistics = statistics and dict(statistics)
        self.value = value and float(value)

    def __str__(self):
        values = [self.name, self.team]
        values.append([pos.name for pos in self.positions])
        if self.statistics:
            stats = [f"{stat.name}: {value}" for stat, value in self.statistics.items()]
            stats = ', '.join(stats)
            stats = f"[{stats}]"
            values.append(stats)
        if self.value:
            values.append(self.value)
        return ', '.join(str(v) for v in values)

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if self.value and other.value:
            return self.value < other.value
        return str(self) < str(other)

    def __hash__(self):
        return hash(str(self))

# class PlayerValue(Player):
#     def __init__(self, name, team, positions, value):
#         self.value = float(value)
#         super().__init__(name, team, positions)

#     @staticmethod
#     def create_from_player(player, value):
#         nm, tm, pos = (player.name, player.team, player.positions)
#         return PlayerValue(nm, tm, pos, value)

#     def __str__(self):
#         return f"{super().__str__()}, {self.value}"

# class PlayerStatistics(Player):
#     def __init__(self, name, team, positions, statistics):
#         self.statistics = dict(statistics)
#         super().__init__(name, team, positions)

#     @staticmethod
#     def create_from_player(player, statistics):
#         nm, tm, pos = (player.name, player.team, player.positions)
#         return PlayerStatistics(nm, tm, pos, statistics)

#     def __str__(self):
#         stats = [f"{stat.name}: {value}" for stat, value in self.statistics.items()]
#         stats = ', '.join(stats)
#         return f"{super().__str__()}, {stats}"

# class PlayerStatisticsValue(Player):
#     def __init__(self, name, team, positions, statistics, value):
#         self.statistics = dict(statistics)
#         self.value = float(value)
#         super().__init__(name, team, positions)

#     @staticmethod
#     def create_from_player(player, statistics, value):
#         nm, tm, pos = (player.name, player.team, player.positions)
#         return PlayerStatisticsValue(nm, tm, pos, statistics, value)

#     @staticmethod
#     def create_from_player_statistics(player, value):
#         nm, tm, pos, stats = (player.name, player.team, player.positions, player.statistics)
#         return PlayerStatisticsValue(nm, tm, pos, stats, value)

#     @staticmethod
#     def create_from_player_value(player, statistics):
#         nm, tm, pos, vl = (player.name, player.team, player.positions, player.value)
#         return PlayerStatisticsValue(nm, tm, pos, statistics, vl)

#     def __str__(self):
#         stats = [f"{stat.name}: {value}" for stat, value in self.statistics.items()]
#         stats = ', '.join(stats)
#         return f"{super().__str__()}, {stats}, {self.value}"

# positions = [get_position_from_str(s) for s in ["2b", "3b"]]
# statistics = [get_statistic_from_str(s) for s in ["AB", "h"]]
# statistics = {s:(i+3) for i,s in enumerate(statistics)}
# p = Player("jerry", "atl", positions, statistics, 5.0)
# print(p)



# class StatisticalValue:
#     def __init__(self, statistic, value):
#         self.statistic = statistic
#         self.value = float(value)

#     def __str__(self):
#         return f"{self.statistic.name}: {self.value}"

#     def __eq__(self, other):
#         return str(self) == str(other)

#     def __ne__(self, other):
#         return not self.__eq__(other)

#     def __hash__(self):
#         return hash(str(self))

# class PlayerWithStatistics:
#     def __init__(self, player, statistics):
#         self.player = player
#         stats = set()
#         for stat in statistics:
#             stats
    
def count_by_position(position_player_dict):
    return {pos: len(position_player_dict[pos]) for pos in position_player_dict}

def get_hitters(players):
    return (p for p in players if is_hitter(p))

def get_pitchers(players):
    return (p for p in players if is_pitcher(p))

def group_by_position(players):
    position_player_dict = defaultdict(set)
    pitcher_cycle = itertools.cycle([Position.SP, Position.RP])
    position_count = {pos:0 for pos in Position}
    for p in players:
        position_to_assign = None
        if p.has_pos(Position.C):
            position_to_assign = Position.C
        elif p.has_all_pos([Position.SS, Position.SECOND_BASE]):
            if position_count[Position.SECOND_BASE] < position_count[Position.SS]:
                position_to_assign = Position.SECOND_BASE
            else:
                position_to_assign = Position.SS
        elif p.has_pos(Position.SECOND_BASE):
            position_to_assign = Position.SECOND_BASE
        elif p.has_pos(Position.SS):
            position_to_assign = Position.SS
        elif p.has_pos(Position.THIRD_BASE):
            position_to_assign = Position.THIRD_BASE
        elif p.has_all_pos([Position.FIRST_BASE, Position.OF]):
            if 2*position_count[Position.FIRST_BASE] < position_count[Position.OF]:
                position_to_assign = Position.FIRST_BASE
            else:
                position_to_assign = Position.OF
        elif p.has_pos(Position.FIRST_BASE):
            position_to_assign = Position.FIRST_BASE
        elif p.has_pos(Position.OF):
            position_to_assign = Position.OF
        elif p.has_all_pos([Position.SP, Position.RP]):
            position_to_assign = next(pitcher_cycle)
        elif p.has_pos(Position.SP):
            position_to_assign = Position.SP
        elif p.has_pos(Position.RP):
            position_to_assign = Position.RP
        else:
            position_to_assign = Position.UTIL
        position_player_dict[position_to_assign].add(p)
        position_count[position_to_assign] += 1
    return position_player_dict


def get_players_from_csv(csv_path, attribute_indices, \
        pos_delimiter, statistic_indices=None, header=True):
    players = set()
    player_values = {}
    player_statistics = {}
    name_index = attribute_indices[Player_Attributes.NAME]
    team_index = attribute_indices[Player_Attributes.TEAM]
    position_index = attribute_indices[Player_Attributes.POSITION]
    value_index = Player_Attributes.VALUE in attribute_indices and \
                  attribute_indices[Player_Attributes.VALUE]
    with open(csv_path, 'r') as csv:
        r = reader(csv)
        if header:
            next(r)
        for l in r:
            line = [unidecode(x) for x in l]
            nm = line[name_index].strip()
            tm = line[team_index]
            pos = line[position_index].split(pos_delimiter)
            pos = [get_position_from_str(s) for s in pos]
            val = (value_index and float(line[value_index])) or None
            stats = {}
            if statistic_indices:
                for stat in statistic_indices:
                    stats[stat] = float(line[statistic_indices[stat]])
            player = Player(name = nm, team = tm, positions = pos)
            players.add(player)
            if val:
                player_values[player] = val
            if stats:
                player_statistics[player] = stats

    return (players, player_values, player_statistics)

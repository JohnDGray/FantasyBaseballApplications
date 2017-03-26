import sys

class Statistic():
    def __init__(self, name: str, invert: bool = False):
        self.name = name
        self.invert = invert

class RateStatistic(Statistic):
    def __init__(self, name: str, invert: bool, qualifier: Statistic):
        Statistic__init__(self, name, invert)
        self.qualifier = qualifier

class League():
    def __init__(teams: int, budget: int, hitter_stats: list, 
            pitcher_stats: list, positions: dict):
        self.teams = teams
        self.budget = budget
        self.hitter_stats = hitter_stats
        self.pitcher_stats = pitcher_stats
        self.positions = positions

class Player:
    def __init__(self, name: str, team: str, positions: list, statistics: dict \
                 hitter: bool):
        self.name = name
        self.team = team
        self.positions = positions
        self.hitter = hitter

class PlayerValue(Player):
    def __init__(player: Player, value: int):
        Player.__init__(self, player.name, player.team, player.positions, \
                player.statistics, player.hitter)
        self.value = value


def sort_player_values(player_values: list) -> list:
    return player_values.sort(key = lambda x: x.value, reverse = True)

def assign_values(players: list, stat_values: dict) -> list:
    output = []
    for player in players:
        value = 0
        for stat in player.statistics:
            if stat in stat_values.keys():
                value_added = player.statistics[stat] * stat_values[stat]
                if isinstance(stat, RateStatistic):
                    value_added *= getattr(player, stat.qualifier.name)
                if stat.invert:
                    value_added *= -1
                value += value_added
        output.append(PlayerValue(player, value))
    return output

def players_to_draft(player_values: list, league: League) -> list:
    player_values = sort_player_values(player_values)
    players = []
    positions = league.positions
    teams = league.teams
    for position in positions:
        num = positions[position] * teams
        players.extend([x for x in player_values if
            x.position == position][0:num])
    return players


def determine_stat_values(players: list, league: League) -> dict:
    def determine_values(players: list, league: League) -> dict:
        scalar = 1000
        output = {}
        for stat in league.statistics:
            all_vals = [getattr(p, stat) for p in players
                    if getattr(p, stat, None) is not None]
            output[stat] = scalar // stdev(all_vals) 
        return output
    players = [PlayerValue(p, 0) for p in players]
    active_players = players_to_draft(players, league)
    old = {stat: 0 for stat in league.statistics}
    new = determine_values(active_players, league)
    while [stat for stat in old if old[stat] != new[stat]]:
        players = assign_values(players, new)
        active_players = players_to_draft(players, league)
        old = new.copy()
        new = determine_values(active_players, league)
    return new

def get_rep_values(player_values: list, league: League) -> dict:
    rep_vals = {}
    player_values = players_to_draft(player_values)
    for position in league.positions:
        val = min([p.value for p in player_values if p.position == position])
        rep_vals[position] = val
    return rep_vals

def get_dollar_vals(player_values: list, league: League, rep_values: dict)
-> list:
    total_value = sum([p.value for p in player_values])
    total_dollars = league.teams * league.budget
    return [PlayerValue(p, total_dollars * (p.value / total_value))
            for p in player_values]
    

def process_league_conf(path: str) -> League:
    with open(path, 'r') as league_conf:
        teams = int(league_conf.next)

def generate_hitter_statistics():
    hitter_stats = []
    ab = Statistic("ab")
    hitter_stats.append(ab)
    hitter_stats.append(Statistic("r"))
    hitter_stats.append(Statistic("hr"))
    hitter_stats.append(Statistic("rbi"))
    hitter_stats.append(Statistic("sb"))
    hitter_stats.append(RateStatistic("avg", False, ab))
    return hitter_stats

def generate_pitcher_statistics():
    pitcher_stats = []
    ip = Statistic("ip")
    pitcher_stats.append(ip)
    pitcher_stats.append(Statistic("w"))
    pitcher_stats.append(Statistic("sv"))
    pitcher_stats.append(Statistic("k"))
    pitcher_stats.append(RateStatistic("era", True, ip))
    pitcher_stats.append(RateStatistic("whip", True, ip))
    return pitcher_stats

def generate_positions():
    positions = {}
    positions['c'] = 1
    positions['1b'] = 1
    positions['2b'] = 1
    positions['3b'] = 1
    positions['ss'] = 1
    positions['of'] = 3
    positions['util'] = 2 
    positions['sp'] = 2
    positions['rp'] = 2
    positions['p'] = 4
    return positions

def generate_players(hitter_path: str, hitter_indices: dict, \
                     pitcher_path: str, pitcher_indices: dict) -> list:
    hitters = []
    with open(hitter_path, 'r') as hitter_file:
        r = reader(hitter_file)
        next(r)
        for line in r:
            name = line[hitter_indices['name']]
            team = line[hitter_indices['team']]
            positions = line[hitter_indices['positions']].split('/')
            positions = [p.strip() for p in positions if p.strip()]
            stats = {}
            for stat, index in hitter_indices:
                stats[stat] = line[index]



            


teams = 12
budget = 260
hitter_stats = generate_hitter_statistics()
pitcher_stats = generate_pitcher_statistics()
positions = generate_positions()

league = League(teams, budget, hitter_stats, pitcher_stats, positions)

hitters = []
pitchers = []



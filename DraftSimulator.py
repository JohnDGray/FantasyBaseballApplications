import Modules.FBClasses as fbclasses
from csv import reader
from collections import namedtuple, defaultdict
from random import shuffle
from statistics import mean

#assumed values

simulation_runs = 100
budget_dollars = 260
total_roster_size = 23

overbid_amounts = [
                   0,
                   0,
                   0,
                   0,
                   0,
                   0,
                   0,
                   0,
                   0,
                   0,
                   0
                  ]

hero_team_overbid_amount = 0

#indices of players to artificially force onto the hero team
#indices are negative so e.g. -3 refers to the third most valuable player
hero_team_strong_player_indices = []

proj_path = "/home/myname/Documents/FantasyValues.csv"

#actual code

Player = fbclasses.Player

def get_players(projections_path):
    players = []
    with open(projections_path, 'r') as projections:
        r = reader(projections)
        for line in r:
            if len(line) < 5:
                continue
            nm, tm, pos, stats, vl = line
            nm = str(nm).strip()
            tm = str(tm).strip()
            pos = pos.split('/')
            vl = int(vl)
            p = Player(nm, tm, pos, None, vl)
            players.append(p)

    players = sorted(players, key=lambda p: p.value)

    return players

players_my_values = get_players(proj_path)
players_yahoo_values = fbclasses.get_yahoo_players()

def get_player_string(player):
    team = fbclasses.translate_team_name(player.team)
    name = player.name.split(' ')
    player_string = name[0][0] + '_'
    player_string += '_'.join(name[1:])
    player_string += '/' + team + '/'
    if fbclasses.is_hitter(player):
        player_string += 'H'
    else:
        player_string += 'P'
    return player_string

my_value_dict = {get_player_string(p): p.value for p in players_my_values}
yahoo_value_dict = {get_player_string(p): p.value for p in players_yahoo_values}

def get_my_value(player):
    player_string = get_player_string(player)
    if player_string in my_value_dict:
        return my_value_dict[player_string]
    elif player_string in yahoo_value_dict:
        return yahoo_value_dict[player_string]
    else:
        return None

def get_yahoo_value(player):
    player_string = get_player_string(player)
    if player_string in yahoo_value_dict:
        return yahoo_value_dict[player_string]
    elif player_string in my_value_dict:
        return my_value_dict[player_string]
    else:
        return None

class Team:
    def __init__(self, *, name, overvalue_amount, draft_value_func=get_my_value):
        self.name = name
        self.budget = budget_dollars
        self.roster_size = total_roster_size
        self.players = []
        self.overvalue_amount = overvalue_amount
        self.draft_value_func = draft_value_func

    def max_bid(self):
        players_to_draft = self.roster_size - len(self.players) - 1
        return self.budget - players_to_draft

    def can_still_draft(self):
        return len(self.players) < self.roster_size

    def make_bid(self, player):
        if not self.can_still_draft():
            return 0
        player_value = self.draft_value_func(player)
        if not player_value:
            player_value = 0
        val = player_value + self.overvalue_amount
        val = max(1, val)
        return min(val, self.max_bid())

    def draft_player(self, player, bid):
        assert self.can_still_draft(), f"Team {self.name} is full"
        assert bid <= self.max_bid(), f"{self.name} Bid over max bid"
        self.players.append(player)
        self.budget -= bid


#simulation
def run_simulation(teams, players, quiet=True):
    players = sorted(players, key=lambda p: p.value, reverse=False)
    hero_team = next(t for t in teams if t.name == 'hero team')

    #draft strong players first
    best_player_indices = hero_team_strong_player_indices[:]
    for best_player_index in best_player_indices:
        best_player = players.pop(best_player_index)
        bid = hero_team.make_bid(best_player)
        bid += hero_team_overbid_amount
        hero_team.draft_player(best_player, bid)
        if not quiet:
            print(f"{hero_team.name} paid {bid} for {best_player.name}, {best_player.value}. They have ${hero_team.budget} left.")

    shuffle(teams)
    while any(players) and any(t for t in teams if t.can_still_draft()):
        player = players.pop()
        bids = tuple((team, team.make_bid(player)) for team in teams)
        drafting_team = bids[0][0]
        max_bid = bids[0][1]
        for team, bid in bids:
            if bid > max_bid:
                drafting_team = team
                max_bid = bid
        if max_bid == 0:
            break
        team_index = teams.index(drafting_team)
        drafting_team = teams.pop(team_index)
        teams.append(drafting_team)
        drafting_team.draft_player(player, max_bid)
        if not quiet:
            print(f"{drafting_team.name} paid {max_bid} for {player.name}, {player.value}. They have ${drafting_team.budget} left.")

    if not quiet:
        print()
    teams.sort(key=lambda t: t.name, reverse=True)

    for team in teams:
        if len(team.players) != total_roster_size:
            num_players = len(team.players)
            budget = team.budget
            msg = f"Team {team.name} has {num_players} players and ${budget} left"
            raise AssertionError(msg)
        total_val = sum(p.value for p in team.players)
        if not quiet:
            print(f"Team {team.name} overvalue amount: {team.overvalue_amount}")
            print(f"Team total value: {total_val}")
            for p in sorted(team.players, key=lambda p: p.value, reverse=True):
                print(p)
            print()


    total_value = 0
    for team in teams:
        for player in team.players:
            total_value += player.value

    if not quiet:
        print(f"Total value {total_value}")
    return teams

# all_players = defaultdict(list)

# for player in players_my_values:
#     team = fbclasses.translate_team_name(player.team)
#     name = player.name.split(' ')
#     player_string = name[0][0] + ' '
#     player_string += ' '.join(name[1:])
#     player_string += '/' + team + '/'
#     if fbclasses.is_hitter(player):
#         player_string += 'H'
#     else:
#         player_string += 'P'
#     all_players[player_string].append(player)
# for player in players_yahoo_values:
#     team = fbclasses.translate_team_name(player.team)
#     name = player.name.split(' ')
#     player_string = name[0][0] + ' '
#     player_string += ' '.join(name[1:])
#     player_string += '/' + team + '/'
#     if fbclasses.is_hitter(player):
#         player_string += 'H'
#     else:
#         player_string += 'P'
#     if player_string in all_players:
#         all_players[player_string].append(player)
# for player_string, player_list in all_players.items():
#     if len(player_list) > 2:
#         print(f"Overmatched player: {player_string} {player_list}")
#     elif len(player_list) < 2:
#         print(f"Unmatched player: {player_string} {player_list}")
# all_players = [ls for player_string, ls in all_players.items() if len(ls) == 2]

team_value_lists = defaultdict(list)
for i in range(1, simulation_runs+1):
    hero_team = Team(name='hero team',overvalue_amount=hero_team_overbid_amount,\
                     draft_value_func=get_my_value)
    teams = [
            #teams using the actual values
            Team(name='team1',overvalue_amount=overbid_amounts[0], \
                 draft_value_func=get_my_value),
            Team(name='team2',overvalue_amount=overbid_amounts[1], \
                 draft_value_func=get_my_value),
            Team(name='team3',overvalue_amount=overbid_amounts[2], \
                 draft_value_func=get_my_value),
            Team(name='team4',overvalue_amount=overbid_amounts[3], \
                 draft_value_func=get_my_value),
            Team(name='team5',overvalue_amount=overbid_amounts[4], \
                 draft_value_func=get_my_value),

            #teams using yahoo values
            Team(name='team6',overvalue_amount=overbid_amounts[5], \
                 draft_value_func=get_yahoo_value),
            Team(name='team7',overvalue_amount=overbid_amounts[6], \
                 draft_value_func=get_yahoo_value),
            Team(name='team8',overvalue_amount=overbid_amounts[7], \
                 draft_value_func=get_yahoo_value),
            Team(name='team9',overvalue_amount=overbid_amounts[8], \
                 draft_value_func=get_yahoo_value),
            Team(name='team10',overvalue_amount=overbid_amounts[9], \
                 draft_value_func=get_yahoo_value),
            Team(name='team11',overvalue_amount=overbid_amounts[10], \
                 draft_value_func=get_yahoo_value),
            hero_team,
            ]
    teams = run_simulation(teams, list(players_my_values),quiet=True)
    for t in teams:
        team_value_lists[t.name].append(sum(p.value for p in t.players))
for t, vl in team_value_lists.items():
    print(f"{t}: {int(round(mean(v for v in vl), 0))}")

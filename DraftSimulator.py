from csv import reader
from collections import namedtuple, defaultdict
from random import shuffle
from statistics import mean

#assumed values

number_of_runs = 100

proj_path = "/home/myname/Downloads/FantasyValues.csv"

Player = namedtuple('Player', 'name team positions value')

class Team:
    def __init__(self, *, name, overvalue):
        self.name = name
        self.budget = 260
        self.roster_size = 23
        self.players = []
        self.overvalue = bool(overvalue)

    def max_bid(self):
        players_to_draft = self.roster_size - len(self.players) - 1
        return self.budget - players_to_draft

    def can_still_draft(self):
        return len(self.players) < self.roster_size

    def make_bid(self, player):
        if not self.can_still_draft():
            return 0
        val = max(1, player.value)
        if self.overvalue:
            val += 1
        return min(val, self.max_bid())

    def draft_player(self, player, bid):
        assert self.can_still_draft(), f"Team {self.name} is full"
        assert bid <= self.max_bid(), f"{self.name} Bid over max bid"
        self.players.append(player)
        self.budget -= bid

def get_players(projections_path):
    players = []
    with open(projections_path, 'r') as projections:
        r = reader(projections)
        for line in r:
            nm, tm, pos, stats, vl = line
            nm = str(nm).strip()
            tm = str(tm).strip()
            pos = pos.split('/')
            vl = int(vl)
            p = Player(nm, tm, pos, vl)
            players.append(p)

    players = sorted(players, key=lambda p: p.value)

    return players

#simulation
def run_simulation(teams, players, quiet=True):
    hero_team = next(t for t in teams if t.name == 'hero team')

    #draft strong players first
    best_player_indices = [-1, -1, -1]
    for best_player_index in best_player_indices:
        best_player = players.pop(best_player_index)
        bid = hero_team.make_bid(best_player)
        bid += 3
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
        if len(team.players) != 23:
            num_players = len(team.players)
            budget = team.budget
            msg = f"Team {team.name} has {num_players} players and ${budget} left"
            raise AssertionError(msg)
        total_val = sum(p.value for p in team.players)
        if not quiet:
            print(f"Team {team.name} used overvalue strategy? {team.overvalue}")
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

players = get_players(proj_path)
team_value_lists = defaultdict(list)
for i in range(1, number_of_runs+1):
    hero_team = Team(name='hero team',overvalue=False)
    teams = [
            Team(name='team1',overvalue=True),
            Team(name='team2',overvalue=True),
            Team(name='team3',overvalue=True),
            Team(name='team4',overvalue=True),
            Team(name='team5',overvalue=True),
            Team(name='team6',overvalue=True),
            Team(name='team7',overvalue=True),
            Team(name='team8',overvalue=True),
            Team(name='team9',overvalue=True),
            Team(name='team10',overvalue=True),
            Team(name='team11',overvalue=True),
            hero_team,
            ]
    teams = run_simulation(teams, list(players))
    for t in teams:
        team_value_lists[t.name].append(sum(p.value for p in t.players))
for t, vl in team_value_lists.items():
    print(f"{t}: {int(round(mean(v for v in vl), 0))}")

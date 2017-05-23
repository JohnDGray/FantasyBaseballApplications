def get_hitter_positions():
    return ['B', 'C', '1B', '2B', '3B', 'SS', 'OF']

class Statistic():
    def __init__(self, name: str, invert: bool=False):
        self.name = name
        self.invert = invert

class RateStatistic(Statistic):
    def __init__(self, name: str, qualifier: Statistic, invert: bool=False):
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
    def __init__(self, name: str, hitter: bool,  team: str=None, \
                 positions: list=None, statistics: dict=None, \
                 value: float=None):
        self.name = name.strip()
        self.team = team and team.strip()
        self.positions = positions and [p.strip() for p in positions \
                                        if p.strip()]
        self.hitter = hitter
        self.value = value

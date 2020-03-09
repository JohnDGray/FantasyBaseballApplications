import sys
from csv import reader

#assumed values

projections_path = '/home/myname/Downloads/FantasyValues.csv'

projection_indices = {
        'name':0,
        'team':1,
        'positions':2,
        'value':4,
}

position_delimiter = '/'

header_lines = 0

#actual code

class Player():
    def __init__(self, name, team, positions, value):
        self.name = name
        self.team = team
        self.positions = [p.strip() for p in positions if p.strip()]
        self.value = int(value)

    def __str__(self):
        result = str(self.name).ljust(20)
        result += str(self.team).ljust(5)
        result += '/'.join(self.positions).ljust(15)
        result += str(self.value).ljust(10)
        return result

class DraftState():
    def __init__(self, budget: int, slots: list, add_index: int,\
                 sub_index: int):
        self.budget = budget
        self.slots = slots
        self._add_index = add_index
        self._sub_index = sub_index

    def copy(self) -> 'DraftState':
        return DraftState(self.budget, self.slots[:], self._add_index, \
                          self._sub_index)

    def get_slots(self) -> list:
        output = self.slots[:]
        output.sort(reverse = True)
        return output

    def draft(self, value: int) -> None:
        if value <= 0:
            raise ValueError("cannot draft a player for less than 1 dollar")
        if value > sum([val-1 for val in self.slots]) + 1:
            raise ValueError("value exceeds maximum allowable value")
        self.budget -= value
        diffs = [abs(value - x) for x in self.slots]
        index = diffs.index(min(diffs))
        del self.slots[index]
        length = len(self.slots)
        if index <= self._add_index:
            self._add_index = (self._add_index - 1) % length
        if index <= self._sub_index:
            self._sub_index = (self._sub_index - 1) % length
        self.adjust_slots()

    def adjust_slots(self):
        diff = self.budget - sum(self.slots)
        length = len(self.slots)
        while diff > 0:
            self._add_index = (self._add_index + 1) % length
            self.slots[self._add_index] += 1
            diff -= 1
        while diff < 0:
            self._sub_index = (self._sub_index + 1) % length
            while self.slots[self._sub_index] == 1:
                self._sub_index = (self._sub_index + 1) % length
            self.slots[self._sub_index] -= 1
            diff += 1

class FirstDraftState(DraftState):
    def __init__(self, roster_size: int, number_of_teams: int, \
                 budget: int, values: list):
        values.sort(reverse=True)
        slots = []
        for i in range(roster_size):
            index = i * number_of_teams
            subset = values[index:index + number_of_teams]
            subset = [max(val, 1) for val in subset]
            subset = [int(val) for val in subset]
            slots.append(sum(subset) // number_of_teams)
        DraftState.__init__(self, budget, slots, -1, -1)
        self.adjust_slots()

def process_projections(projections_path: str) -> list:
    players = []
    with open(projections_path, 'r') as projections:
        r = reader(projections)
        for _ in range(header_lines):
            next(r)
        for line in r:
            if not line[4]:
                continue
            nm = line[projection_indices['name']]
            tm = line[projection_indices['team']]
            ps = line[projection_indices['positions']]
            ps = ps.split(position_delimiter)
            vl = line[projection_indices['value']]
            p = Player(nm, tm, ps, vl)  
            players.append(p)
    return players

players = process_projections(projections_path)
values = [p.value for p in players]
draft_states = []
draft_states.append(FirstDraftState(23, 12, 260, values))
values = None

def get_max_bid(slots):
    return 1 + sum([x-1 for x in slots])

def modify_value(slots, value):
    max_bid = get_max_bid(slots) 
    discount_value = 0.9 * value
    highest_value = max(slots)
    diff = discount_value - highest_value
    diff /= 10
    diff *= 9
    return min(max_bid, discount_value, highest_value+diff)

while True:
    last_state = draft_states[-1]
    print(last_state.get_slots())
    print()
    next_value = input("Enter a value\n")
    print()
    try:
        next_value = int(next_value)
    except ValueError:
        arguments = next_value.split()
        results = []
        if not len(arguments):
            print("please supply an argument")
            print("examples:")
            print("-u to undo last change")
            print("-p 2b to search for second basemen")
            print("stant to search for players with 'stant' in their names")
            continue
        elif arguments[0].startswith("-u"):
            if len(draft_states) > 1:
                print("Undoing last pick")
                draft_states.pop()
            else:
                print("Cannot undo since nothing has happened yet")
            continue
        elif arguments[0].startswith("-p"):
            if len(arguments) < 2:
                print("Usage: -p {position}")
                continue
            position_to_get = arguments[1].lower()
            results = [p for p in players if any([pos for pos in p.positions if position_to_get in pos.lower()])]
        else:
            results = [p for p in players if next_value.lower() in p.name.lower()]
        results = [r for r in results if r.value > 0 or abs(r.value) < 10]
        results = results[:40]
        header_display = str('name').ljust(20)
        header_display += str('team').ljust(10)
        header_display += str('mod val').ljust(10)
        header_display += str('act val').ljust(10)
        header_display += str('pos').ljust(30)
        print(header_display)
        for result in results:
            display_value = str(result.name).ljust(20)
            display_value += str(result.team).ljust(10)
            display_value += \
                str(int(modify_value(last_state.slots, result.value))).ljust(10)
            display_value += str(result.value).ljust(10)
            display_value += '/'.join(result.positions).ljust(30)
            print(display_value)
        print()
        continue
    next_state = last_state.copy()
    try:
        next_state.draft(next_value)
    except ValueError as e:
        print(str(e))
        print()
        continue
    draft_states.append(next_state)


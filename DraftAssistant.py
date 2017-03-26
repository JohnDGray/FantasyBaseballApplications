import sys
from csv import reader

class Player():
    def __init__(self, name, team, positions, value):
        self.name = name
        self.team = team
        self.positions = [p.strip() for p in positions if p.strip()]
        self.value = float(value)

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
        next(r)
        for line in r:
            positions = line[3].split('/')
            p = Player(line[1], line[2], positions, line[5])  
            players.append(p)
    return players

players = process_projections(sys.argv[1])
values = [p.value for p in players]
draft_states = []
draft_states.append(FirstDraftState(23, 12, 260, values))
values = None

def modify_value(slots, value):
    highest_value = max(slots)
    if value <= highest_value:
        return value
    diff = value - highest_value
    diff //= 3
    diff *= 2
    return highest_value + diff

while True:
    last_state = draft_states[-1]
    print(last_state.get_slots())
    print()
    next_value = input("Enter a value\n")
    print()
    try:
        next_value = int(next_value)
    except ValueError:
        if next_value and len(next_value) == 4 and \
           next_value.lower().strip() == "undo" and \
           len(draft_states) > 1:
            print("Undoing last pick")
            draft_states.pop()
            continue
        results = [p for p in players if next_value.lower() in p.name.lower()]
        results = [p for p in results if p.value > 0 or abs(p.value) < 10]
        for result in results:
            display_value = str(result.name).ljust(20)
            display_value += str(result.team).ljust(5)
            display_value += '/'.join(result.positions).ljust(15)
            display_value += \
                str(modify_value(last_state.slots, result.value)).ljust(10)
            display_value += str(result.value).ljust(10)
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


import Modules.FBClasses
import itertools
import re
import statistics
from csv import reader
from unidecode import unidecode

#assumed values

position_delimiter = '/'

hitter_value_indices = {
    Modules.FBClasses.Player_Attributes.NAME:1,
    Modules.FBClasses.Player_Attributes.TEAM: 2,
    Modules.FBClasses.Player_Attributes.POSITION:5
}

hitter_statistic_indices = {
        Modules.FBClasses.Statistic.G:6,
        Modules.FBClasses.Statistic.PA:7,
        Modules.FBClasses.Statistic.AB:8,
        Modules.FBClasses.Statistic.R:9,
        Modules.FBClasses.Statistic.HR:10,
        Modules.FBClasses.Statistic.RBI:11,
        Modules.FBClasses.Statistic.SB:12,
        Modules.FBClasses.Statistic.H:13,
        Modules.FBClasses.Statistic.AVG:24
}

pitcher_value_indices = {
    Modules.FBClasses.Player_Attributes.NAME:1,
    Modules.FBClasses.Player_Attributes.TEAM: 2,
    Modules.FBClasses.Player_Attributes.POSITION:3
}

pitcher_statistic_indices = {
        Modules.FBClasses.Statistic.G:5,
        Modules.FBClasses.Statistic.GS:6,
        Modules.FBClasses.Statistic.IP:9,
        Modules.FBClasses.Statistic.W:10,
        Modules.FBClasses.Statistic.SV:12,
        Modules.FBClasses.Statistic.HLD:13,
        Modules.FBClasses.Statistic.ERA:14,
        Modules.FBClasses.Statistic.WHIP:16,
        Modules.FBClasses.Statistic.K:17
}

hitter_projections_path = "/home/myname/Downloads/SteamerHitters.csv"
pitcher_projections_path = "/home/myname/Downloads/SteamerPitchers.csv"
yahoo_csv_path = "/home/myname/Downloads/Yahoo.csv"

yahoo_name_column=0
yahoo_dollar_column=2

num_to_draft=12*23
draft_dollars=12*260

#end assumed values

yahoo_players = []
with open(yahoo_csv_path, 'r') as yahoo:
    r = reader(yahoo)
    next(r)
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
        nm = m.group(1)
        tm = m.group(2)
        pos = [x.strip() for x in m.group(3).split(',')]
        pos = [Modules.FBClasses.get_position_from_str(x) for x in pos]

        vl = unidecode(line[yahoo_dollar_column])
        m = re.search('(.*\$\s*)(.*)', vl, re.IGNORECASE)
        vl = float(m.group(2))

        player = Modules.FBClasses.Player(name=nm, team=tm, positions=pos, value=vl)
        yahoo_players.append(player)

# for p_v in yahoo_players:
#     print(p_v[0])
#     print(f"${p_v[1]}")

yahoo_players = sorted(yahoo_players, reverse=True)
yahoo_players = yahoo_players[0:num_to_draft]
total_value = sum(p.value for p in yahoo_players)
print(total_value)
scalar = draft_dollars / total_value

scalar_func = lambda value: scalar * value
yahoo_players = list(Modules.FBClasses.update_player_values(yahoo_players, scalar_func))
for p in yahoo_players:
    print(p)
total_value = sum(p.value for p in yahoo_players)
print(f"total value: {total_value}")
yahoo_by_position = Modules.FBClasses.group_by_position(yahoo_players)
print(yahoo_by_position)
# assign_primary_positions(yahoo_players)

#yahoo_hitters = [p for p in yahoo_players if p.is_hitter()]
#yahoo_pitchers = [p for p in yahoo_players if p.is_pitcher()]
#yahoo_catchers = [p for p in yahoo_players if p.has_primary_pos(Position.C)]
#yahoo_first_baseman = [p for p in yahoo_players if p.has_primary_pos(Position.FIRST_BASE)]
#yahoo_second_baseman = [p for p in yahoo_players if p.has_primary_pos(Position.SECOND_BASE)]
#yahoo_third_baseman = [p for p in yahoo_players if p.has_primary_pos(Position.THIRD_BASE)]
#yahoo_shortstops = [p for p in yahoo_players if p.has_primary_pos(Position.SS)]
#yahoo_outfielders = [p for p in yahoo_players if p.has_primary_pos(Position.OF)]
#yahoo_utility_players = [p for p in yahoo_players if p.has_primary_pos(Position.UTIL)]
#yahoo_starting_pitchers = [p for p in yahoo_players if p.has_primary_pos(Position.SP)]
#yahoo_relief_pitchers = [p for p in yahoo_players if p.has_primary_pos(Position.RP)]

#position_dollar_values = {
#        Position.HITTER:sum(p.dollar_value for p in yahoo_hitters),
#        Position.PITCHER:sum(p.dollar_value for p in yahoo_pitchers),
#        Position.C:sum(p.dollar_value for p in yahoo_catchers),
#        Position.FIRST_BASE:sum(p.dollar_value for p in yahoo_first_baseman),
#        Position.SECOND_BASE:sum(p.dollar_value for p in yahoo_second_baseman),
#        Position.THIRD_BASE:sum(p.dollar_value for p in yahoo_third_baseman),
#        Position.SS:sum(p.dollar_value for p in yahoo_shortstops),
#        Position.OF:sum(p.dollar_value for p in yahoo_outfielders),
#        Position.UTIL:sum(p.dollar_value for p in yahoo_utility_players),
#        Position.SP:sum(p.dollar_value for p in yahoo_starting_pitchers),
#        Position.RP:sum(p.dollar_value for p in yahoo_relief_pitchers)
#}

#position_count = {
#        Position.HITTER:sum(1 for _ in yahoo_hitters),
#        Position.PITCHER:sum(1 for _ in yahoo_pitchers),
#        Position.C:sum(1 for _ in yahoo_catchers),
#        Position.FIRST_BASE:sum(1 for _ in yahoo_first_baseman),
#        Position.SECOND_BASE:sum(1 for _ in yahoo_second_baseman),
#        Position.THIRD_BASE:sum(1 for _ in yahoo_third_baseman),
#        Position.SS:sum(1 for _ in yahoo_shortstops),
#        Position.OF:sum(1 for _ in yahoo_outfielders),
#        Position.UTIL:sum(1 for _ in yahoo_utility_players),
#        Position.SP:sum(1 for _ in yahoo_starting_pitchers),
#        Position.RP:sum(1 for _ in yahoo_relief_pitchers)
#}

#for k, v in position_count.items():
#    print(k, v)

#hitters = get_players_from_csv(hitter_projections_path, hitter_value_indices,\
#        hitter_statistic_indices, position_delimiter)
#pitchers = get_players_from_csv(pitcher_projections_path, pitcher_value_indices,\
#        pitcher_statistic_indices, position_delimiter)
#all_players = hitters + pitchers
#steamer_collection = Player_Collection(all_players)
#steamer_collection.reduce_by_counts(position_count)
##all_players = select_players(all_players, position_count)
##temp_hitters = [p for p in all_players if p.is_hitter()]
##temp_pitchers = [p for p in all_players if p.is_pitcher()]


#print(steamer_collection.get_player_count)
#for p in steamer_collection.get_all_players():
#    print(p)
##print(sum(1 for pos, plyrs in all_players.items() for _ in plyrs))
##for p in all_players:
#    #print(p)

##all_stats = collect_stats(all_players)
##stat_res = stat_results(all_stats)

##for s in stat_res:
#    #print(s, stat_res[s])




##for hitter in hitters:
#    #print(hitter)
##for pitcher in pitchers:
#    #print(pitcher)







python3 test2.py > TEMPRAZZBALL

teams=( GayFishYo MadDogs PuppyIII PillarsOfSociety Beowulf \
          Piranhas Munique IndyFighters BryzzoForMVP TeamName \
          PatStone ShanesSwellTeam )

for i in {1..12}
do
    python3 test.py $i B sum > "/home/simon/Documents/FantasyBaseballProject/\
Output/${teams[$i-1]}"
    python3 test.py $i B list >> "/home/simon/Documents/FantasyBaseballProject/\
Output/${teams[$i-1]}"
    echo "" >> "/home/simon/Documents/FantasyBaseballProject/\
Output/${teams[$i-1]}"
    python3 test.py $i P sum >> "/home/simon/Documents/FantasyBaseballProject/\
Output/${teams[$i-1]}"
    python3 test.py $i P list >> "/home/simon/Documents/FantasyBaseballProject/\
Output/${teams[$i-1]}"
done

positions=( B C 1B 2B 3B SS OF P SP RP )

for i in {0..9}
do
    python3 test.py A ${positions[$i]} list > "/home/simon/Documents/\
FantasyBaseballProject/Output/${positions[$i]}"
done

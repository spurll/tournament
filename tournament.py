# Written by Gem Newman. This work is licensed under a Creative Commons
# Attribution-NonCommercial-ShareAlike 3.0 Unported License.

# To Implement:
#
#   An "undo" fuction would be fairly trivial (and useful!) to implement!
#   Just keep a deep copy of the players set!
#
#   Make this a webPy thing.
#
#   Add full logging, including the IP address of whomever connects (for
#   stats-gathering purposes).
#
#   Should walk a tree and find optimal pairings among players, then randomly
#   select between optimals.
#
# Known Bugs:
#
#   When editing pairings involving a bye, the message says "...as a result,
#   ______ is now paired with BYE" instead of "...now has a BYE".
#
#   Pairings can result in multiple byes if bottom-rung players have
#   already played each other.
#
#   Players can hypothetically achieve multiple byes (only if they suck).
#
#   Manual pairing says: "As a result, Curt is now paired with BYE."

# More information about byes, tiebreakers, etc. can be found here:
# http://www.wizards.com/ContentResources/Wizards/WPN/Main/Documents/Magic_The_Gathering_Tournament_Rules_PDF2.pdf


import argparse, random, math
from table import table, menu
from player import Player


DEFAULT_PLAYERS = {"Gem", "Curt", "Matt", "Cozmin", "Eric", "Brendan",
                   "Dustin", "Dale", "Bhavek", "Mike", "Aron", "Nick"}

DEFAULT_STRING = "Richard Garfield"
BYE = Player("BYE", is_bye_player=True)
IDEAL_TABLE = 8


def tournament(players=None):
    """
    Runs a Magic limited event (draft or sealed).
    players: List of player names (defaults to DEFAULT_PLAYERS, with the option
             to change the list).
    """
    if not players:
        players = DEFAULT_PLAYERS
        change = DEFAULT_STRING
        while change:
            change = menu("Players", players, footer="Enter a name to add or "
                          "remove a player (ENTER for none).")
            if change and (change in players):
                players -= {change}
            elif change:
                players.add(change)

    players = {p: Player(p) for p in players}

    items = MAIN_MENU.keys()
    items.sort()
    call = menu("Main Menu", items, input_range=range(1, len(items) + 1))
    while MAIN_MENU[items[int(call) - 1]]:
        MAIN_MENU[items[int(call) - 1]](players)
        call = menu("Main Menu", items, input_range=range(1, len(items) + 1))


def seat_players(players):
    active = active_players(players)
    names = active.keys()
    random.shuffle(names)

    table_count = number_of_tables(len(active))
    table_size = int(math.ceil(float(len(active)) / table_count))

    print "Players: {}".format(len(active))
    print "Tables: {}".format(table_count)
    print "Seats per Table: {}".format(table_size)

    rows = []

    for table in xrange(table_count):
        for seat in xrange(table_size):
            index = (table * table_size) + seat
            if len(active) <= index:
                break
            else:
                active[names[index]].table = table + 1
                active[names[index]].seat = seat + 1
                rows.append((table + 1, seat + 1, names[index]))

    menu("Seating", *zip(*rows), headers=["Table", "Seat", "Player"],
         footer="ENTER to continue.")


def pair_players(players):
    active = active_players(players)
    reported = [active[k].reported for k in active.keys()]
    pairs = []

    # Warn if some players have reported and some haven't.
    if any(reported) and not all(reported):
        print "Warning: Reporting is incomplete! Are you sure you want to "   \
              "re-pair?"
        response = DEFAULT_STRING
        while response[0].lower() not in ['y', 'n']:
            response = raw_input(">> ")

        if response[0].lower() == 'n':
            return

    # Begin a new round, by setting everyone's "reported" status to false.
    for p in active.keys():
        active[p].reported = False

    # If no one has any points, it's the first round, so pair people by seat.
    bye_player = None
    player_list = active.values()
    player_count = len(active)
    table = 1
    if sum([p.points() for p in player_list]) == 0:
        if any([p.seat == None for p in player_list]):
            print "Warning: You must seat players before pairing! (ENTER to " \
                  "continue.)"
            raw_input(">> ")
            return

        # For each draft table, pair players as far as possible. Then pair any
        # leftover players together between tables. Then, if anyone is left
        # that player gets a bye.

        unpaired = []
        draft_tables = [[p for p in player_list if p.table == t] for t in
                        {p.table for p in player_list}]
        for current_players in draft_tables:
            current_players.sort(key=lambda p: p.seat)
            player_count = len(current_players)

            if player_count % 2 != 0:
                # The player in the last seat is not paired at this table.
                unpaired.append(current_players[player_count - 1])
                player_count -= 1

            # Each player will face an opponent halfway around their table.
            for i in xrange(player_count / 2):
                opponent = current_players[(i + (player_count / 2)) %
                                           player_count]

                current_players[i].opponent = opponent
                opponent.opponent = current_players[i]
                pairs.append((table, current_players[i].name, opponent.name))

                current_players[i].table = table
                opponent.table = table
                table += 1

        player_count = len(unpaired)
        # Pair any players that couldn't be paired with their own draft tables.
        if player_count:
            if player_count % 2 != 0:
                # The player in the last seat is not paired at this table.
                bye_player = unpaired[player_count - 1]
                player_count -= 1

            # Each player will face an opponent halfway around their table.
            for i in xrange(player_count / 2):
                opponent = unpaired[(i + (player_count / 2)) % player_count]

                unpaired[i].opponent = opponent
                opponent.opponent = unpaired[i]
                pairs.append((table, unpaired[i].name, opponent.name))

                unpaired[i].table = table
                opponent.table = table
                table += 1

    # First, assign BYE to worst player that hasn't had a BYE. Then, for each
    # player, generate a list of opponents they could play... Not sure that'd
    # work, and I don't have time to implement it... So never mind!

    # Pair based upon points.
    else:
        # player_list.sort(key=lambda p: p.points(), reverse=True)
        player_list.sort(reverse=True)

        # Each player faces an opponent not previously faced of similar rank.
        for i in xrange(player_count):
            for j in xrange(i + 1, player_count):
                if not player_list[i].opponent and not                        \
                        player_list[j].opponent and player_list[i].name not in\
                        [p.name for p in player_list[j].past_opponents]:
                    player_list[i].opponent = player_list[j]
                    player_list[j].opponent = player_list[i]

                    pair = (table, player_list[i].name, player_list[j].name)
                    pairs.append(pair)

                    player_list[i].table = table
                    player_list[j].table = table
                    table += 1
                    break
            else:
                if not player_list[i].opponent:
                    bye_player = player_list[i]

    if bye_player:
        pairs.append((table, bye_player.name, BYE))
        bye_player.opponent, BYE.opponent = BYE, bye_player
        bye_player.table, BYE.table = table, table

    menu("Pairings", *zip(*pairs), headers=["Table", "Player", "Opponent"],
         footer="ENTER to continue.")


def edit_pairings(players):
    active = active_players(players)
    player_list = active.values()
    reported = [p.reported for p in player_list]
    opponents = [p.opponent for p in player_list]

    if any(reported):
        print "Warning: You cannot edit pairings after reporting has begun!"  \
              " (ENTER to continue.)"
        raw_input(">> ")
        return

    if not any(opponents):
        print "Warning: You must pair players before editing the pairings."   \
              " (ENTER to continue.)"
        raw_input(">> ")
        return

    while True:
        player_list.sort(key=lambda p: p.table)
        pairs = [(player_list[i].table, player_list[i].name,
                 player_list[i].opponent.name) for i in range(0,
                 len(player_list), 2)]

        player_1 = menu("Pairings", *zip(*pairs), headers=["Table", "Player",
                        "Opponent"], footer="Enter a player's name to change "
                        "that player's opponent. (ENTER to cancel.)",
                        input_range=[p.name for p in player_list] + [""])
        if not player_1: return

        other_players = [p.name for p in player_list if p.name != player_1]
        print "Pair {} with which player? (ENTER to cancel.)".format(player_1)

        player_2 = DEFAULT_STRING
        while player_2:
            player_2 = raw_input(">> ")
            if player_2 in other_players:
                player_1, player_2 = players[player_1], players[player_2]
                opponent_1, opponent_2 = player_1.opponent, player_2.opponent

                player_1.opponent = player_2
                player_2.opponent = player_1
                player_2.table = player_1.table

                opponent_1.opponent = opponent_2
                opponent_2.opponent = opponent_1
                opponent_1.table = opponent_2.table

                print "{} is paired with {}. As a result, {} is now paired "  \
                      "with {}. (ENTER to continue.)".format(player_1.name,
                      player_1.opponent.name, opponent_1.name,
                      opponent_1.opponent.name)
                raw_input(">> ")
                break


def report_results(players):
    active = active_players(players)
    reported = [active[k].reported for k in active.keys()]

    while not all(reported):
        pairs, choices = [], []
        for p in active.values():
            if p.opponent and not p.reported:
                if p.opponent is BYE:
                    p.reported = True
                    p.byes += 1
                    p.opponent = None
                elif p.name not in [i.name for sub in pairs for i in sub if
                                    isinstance(i, Player)]:
                    pairs.append((p.table, p, p.opponent))
                    choices.append(p.table)

        if not pairs:
            print "Warning: You must pair players before reporting! (ENTER "  \
                  "to continue.)"
            raw_input(">> ")
            return

        pairs.sort()    # Sort by table number.
        choices.sort()

        choice = menu("Report Match Results", *zip(*pairs), 
                      headers=["Table", "Player", "Opponent"],
                      footer="Select a table to report (ENTER to cancel).",
                      input_range=choices+[""])
        if not choice: return

        # Convert from table number to list index.
        choice = choices.index(int(choice))
        p = pairs[choice][1]
        wins = menu("Match Results: {} versus {}".format(p.name,
                    p.opponent.name), ["How many games did {} "
                    "win?".format(p.name)], footer="ENTER to cancel.",
                    input_range=[0, 1, 2, ""])
        if not wins: continue
        losses = menu("Match Results: {} versus {}".format(p.name,
                      p.opponent.name), ["How many games did {} "
                      "win?".format(p.opponent.name)], footer="ENTER to "
                      "cancel.", input_range=[0, 1, 2, ""])
        if not losses: continue
        draws = menu("Match Results: {} versus {}".format(p.name,
                     p.opponent.name), ["How many games did ended in a draw?"],
                     footer="ENTER to cancel.", input_range=[0, 1, 2, ""])
        if not draws: continue

        wins, losses, draws = int(wins), int(losses), int(draws)
        games = sum([wins, losses, draws])
        if games < 1 or games > 3:
            print "Warning: Matches are best two of three. You have reported" \
                  " an invalid number of matches. (ENTER to continue.)"
            raw_input(">> ")
            continue

        p.matches += 1
        p.opponent.matches += 1
        p.games += games
        p.opponent.games += games

        p.match_wins += wins > losses
        p.opponent.match_wins += wins < losses
        p.match_draws += wins == losses
        p.opponent.match_draws += wins == losses

        p.game_wins += wins
        p.opponent.game_wins += losses
        p.game_draws += draws
        p.opponent.game_draws += draws
        
        p.reported, p.opponent.reported = True, True
        p.past_opponents.append(p.opponent)
        p.opponent.past_opponents.append(p)
        p.opponent.opponent = None
        p.opponent = None

        reported = [active[k].reported for k in active.keys()]

    print "All players have reported. (ENTER to continue.)"
    raw_input(">> ")

 
def standings(players):
    player_list = players.values()
    player_list.sort(reverse=True)

    names = [p.name for p in player_list]
    points = [p.points() for p in player_list]
    tiebreaker_1 = [p.tb_1() for p in player_list]
    tiebreaker_2 = [p.tb_2() for p in player_list]
    tiebreaker_3 = [p.tb_3() for p in player_list]
    dropped = ["" if p.active else "Yes" for p in player_list]

    menu("Standings", names, points, tiebreaker_1, tiebreaker_2, tiebreaker_3,
         dropped, footer="ENTER to continue.", headers=["Player", "Points",
         "TB 1", "TB 2", "TB 3", "Dropped?"])


def player_stats(players):
    p = DEFAULT_STRING
    while p:
        p = menu("Display Player Stats", players.keys(), ["" if
                    players[k].active else "Yes" for k in players.keys()],
                    headers=["Player", "Dropped?"], footer="Enter a name to "
                    "view that player's stats. (ENTER for none).",
                    input_range=players.keys()+[""])
        if p: players[p].display()


def drop_player(players):
    drop = DEFAULT_STRING
    while drop:
        drop = menu("Drop Players", players.keys(), ["" if players[k].active
                    else "Yes" for k in players.keys()], headers=["Player",
                    "Dropped?"], footer="Enter a name to drop that player "
                    "(ENTER for none).", input_range=players.keys()+[""])
        if drop: players[drop].drop()


def is_int(value):
    try: 
        int(value)
        return True
    except ValueError:
        return False


def active_players(players):
    return {players[name].name:players[name] for name in players.keys() if
            players[name].active}


def number_of_tables(player_count):
    """
    Players should be seated such that tables have as close to eight players
    each as possible.
    """
    tables = range(1, player_count + 1)
    diff = [abs(math.floor(player_count / i) - IDEAL_TABLE) for i in tables]
    return int(diff.index(min(diff))) + 1


if __name__ == "__main__":
    MAIN_MENU = {"1. Seat Players": seat_players,
                 "2. Pair Players": pair_players,
                 "3. Edit Pairings": edit_pairings,
                 "4. Report Match Results": report_results,
                 "5. Standings": standings,
                 "6. Display Player Stats": player_stats,
                 "7. Drop Player": drop_player,
                 "8. Exit": None}

    parser = argparse.ArgumentParser(description="Runs a Magic: The Gathering "
                                     "limited event (sealed or draft).")
    parser.add_argument("player", metavar="player", type=str, nargs="*",
                           help="Player name.", default=None)
    tournament(parser.parse_args().player)

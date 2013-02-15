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
# Known Bugs:
#
#   Pairings can result in multiple byes if bottom-rung players have
#   already played each other.
#
#   Players can hypothetically achieve multiple byes (only if they suck).
# 
#   If players have been seated, and THEN people drop (and are not reseated)
#   pairings are FUCKED.


# More information about byes, tiebreakers, etc. can be found here:
# http://www.wizards.com/ContentResources/Wizards/WPN/Main/Documents/Magic_The_Gathering_Tournament_Rules_PDF2.pdf


import argparse, random, math


DEFAULT_PLAYERS = {"Gem", "Curt", "Matt", "Cozmin", "Eric", "Brendan",
                   "Dustin", "Dale", "Bhavek", "Mike", "Aron", "Nick"}

DEFAULT_STRING = "Richard Garfield"
BYE_TEXT = "BYE"
IDEAL_TABLE = 8


class Player:
    def __init__(self, name):
        self.name = name
        self.matches = 0            # Does not include byes.
        self.match_wins = 0
        self.match_draws = 0
        self.games = 0              # Does not include byes.
        self.game_wins = 0
        self.game_draws = 0
        self.byes = 0               # Treated as a match win (2-0).
        self.table = None
        self.seat = None
        self.opponent = None        # May contain BYE_TEXT.
        self.past_opponents = []    # Does not include byes.
        self.active = True
        self.reported = False

    def __repr__(self):
        return self.name

    def __lt__(self, other):
        if not isinstance(other, Player):
            return False

        if self.active < other.active:
            return True
        elif self.active > other.active:
            return False

        if self.points() < other.points():
            return True
        elif self.points() > other.points():
            return False

        if self.opponent_match_win_percentage() <                             \
                other.opponent_match_win_percentage():
            return True
        elif self.opponent_match_win_percentage() >                           \
                other.opponent_match_win_percentage():
            return False

        if self.game_win_percentage() < other.game_win_percentage():
            return True
        elif self.game_win_percentage() > other.game_win_percentage():
            return False

        if self.opponent_game_win_percentage() <                              \
                other.opponent_game_win_percentage():
            return True
        else:
            return False

    def __eq__(self, other):
        if not isinstance(other, Player):
            return False
        return not self < other and not other < self

    def __ne__(self, other):
        if not isinstance(other, Player):
            return False
        return self < other or other < self

    def __ge__(self, other):
        if not isinstance(other, Player):
            return False
        return not self < other

    def __le__(self, other):
        if not isinstance(other, Player):
            return False
        return not other < self

    def __gt__(self, other):
        if not isinstance(other, Player):
            return False
        return other < self

    def drop(self):
        self.active = False

    def points(self):
        return self.match_points()

    def tb_1(self):
        return self.opponent_match_win_percentage()

    def tb_2(self):
        return self.game_win_percentage()

    def tb_3(self):
        return self.opponent_game_win_percentage()

    def match_points(self):
        # A bye is considered a match win, and is worth 3 match points.
        return (3 * (self.match_wins + self.byes)) + self.match_draws

    def game_points(self):
        # A bye is considered two game wins, and is worth 6 game points.
        return (3 * (self.game_wins + (2 * self.byes))) + self.game_draws

    def match_win_percentage(self):
        if self.matches == 0:
            percent = 0.33
        else:
            percent = self.match_points / (self.matches + self.byes)
        return max(round(percent), 0.33)

    def game_win_percentage(self):
        if self.games == 0:
            percent = 0.33
        else:
            percent = self.game_points / (self.games + (2 * self.byes))
        return max(round(percent), 0.33)

    def opponent_match_win_percentage(self):
        if self.matches == 0: return 0.33
        percentage = [o.match_win_percentage() for o in self.past_opponents]
        return round(sum(percentage) / len(percentage), 2)

    def opponent_game_win_percentage(self):
        if self.games == 0: return 0.33
        percentage = [o.game_win_percentage() for o in self.past_opponents]
        return round(sum(percentage) / len(percentage), 2)


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
    call = menu("Main Menu", items, input_range=range(1,len(items) + 1))
    while MAIN_MENU[items[int(call) - 1]]:
        MAIN_MENU[items[int(call) - 1]](players)
        call = menu("Main Menu", items, input_range=range(1,len(items) + 1))


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
    bye = None
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
                bye = unpaired[player_count - 1]
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
                    bye = player_list[i]

    if bye:
        pairs.append((table, bye.name, BYE_TEXT))
        bye.opponent = BYE_TEXT
        bye.table = table

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
                 len(player_list) - 1, 2)]

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
        pairs = []
        for p in active.values():
            if p.opponent and not p.reported:
                if p.opponent == BYE_TEXT:
                    p.reported = True
                    p.byes += 1
                    p.opponent = None
                elif p.name not in [i.name for sub in pairs for i in sub if
                                    isinstance(i, Player)]:
                    pairs.append((p.table, p, p.opponent))

        if not pairs:
            print "Warning: You must pair players before reporting! (ENTER "  \
                  "to continue.)"
            raw_input(">> ")
            return

        pairs.sort()    # Sort by table number.

        choice = menu("Report Match Results", *zip(*pairs), 
                      headers=["Table", "Player", "Opponent"],
                      footer="Select a table to report (ENTER to cancel).",
                      input_range=range(1,len(pairs)+1)+[""])
        if not choice: return

        p = pairs[int(choice) - 1][1]
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

        p.game_wins = wins
        p.opponent.game_wins = losses
        p.game_draws = draws
        p.opponent.game_draws = draws
        
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


def drop_player(players):
    drop = DEFAULT_STRING
    while drop:
        drop = menu("Drop Players", players.keys(), ["" if players[k].active
                    else "Yes" for k in players.keys()], headers=["Player",
                    "Dropped?"], footer="Enter a name to drop that player "
                    "(ENTER for none).", input_range=players.keys()+[""])
        if drop: players[drop].drop()


def menu(title, *items, **options):
    """
    Creates a menu, asking the user to select an option, then returns that
    option.

    title: string, the title of the menu.
    *items: list, the menu items to display; multiple lists are acceptable.
    **headers: list, column headers for each column in items.
    **footer: string, the footer to display before the prompt at the bottom.
    **input_range: list, a list of acceptable inputs; if user input string is
                   not in this list, input is rejected.
    """
    headers = options["headers"] if "headers" in options.keys() else None
    footer = options["footer"] if "footer" in options.keys() else None
    input_range = [str(i) for i in options["input_range"]] if "input_range"   \
                   in options.keys() else None

    table(title, *items, headers=headers, footer=footer)

    choice = raw_input(">> ")
    while input_range and not choice in input_range:
        choice = raw_input(">> ")

    return choice


def table(title, *columns, **options):
    """
    Creates a table.
    title: string, the title of the table.
    *columns: tuples, with each tuple representing a column (and each item in
              each tuple representing a cell in the table).
    **headers: list, column headers for each column in items.
    **footer: string, the footer to display before the prompt at the bottom.
    """
    headers = options["headers"] if "headers" in options.keys() else None
    footer = options["footer"] if "footer" in options.keys() else None

    column_widths = [max(max([len(str(item)) for item in c]), 1) for c in
                     columns]
    if headers:
        column_widths = [max(w) for w in zip(column_widths, [len(h) for h in
                         headers])]

    total_width = sum(column_widths) + (3 * (len(column_widths) - 1))
    if total_width < len(title):
        diff = len(title) - total_width
        column_widths[0] += diff
        total_width += diff

    rows = zip(*columns)

    print "+{}+".format("-" * (total_width + 2))
    print "| {:^{}} |".format(title, total_width)

    dividers = ["-" * (w + 2) for w in column_widths]
    print "+{}+".format("+".join(dividers))

    if headers:
        cells = [" {:{}} |".format(*column_width) for column_width in
                 zip(headers, column_widths)]
        print "".join(["|"] + cells)
        print "+{}+".format("+".join(dividers))

    for row in rows:
        cells = [" {:{}} |".format(*column_width) for column_width in zip(row,
                 column_widths)]
        print "".join(["|"] + cells)

    print "+{}+".format("+".join(dividers))

    if footer:
        print footer


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
                 "6. Drop Player": drop_player,
                 "7. Exit": None}

    parser = argparse.ArgumentParser(description="Runs a Magic: The Gathering "
                                     "limited event (sealed or draft).")
    parser.add_argument("player", metavar="player", type=str, nargs="*",
                           help="Player name.", default=None)
    tournament(parser.parse_args().player)

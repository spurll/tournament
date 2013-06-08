class Player:
    def __init__(self, name, is_bye_player=False):
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
        self.opponent = None
        self.past_opponents = []    # Does not include byes.
        self.active = True
        self.reported = False
        self.is_bye_player = is_bye_player

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
            percent = self.match_points() / (3.0 * (self.matches + self.byes))
        return max(round(percent, 2), 0.33)

    def game_win_percentage(self):
        if self.games == 0:
            percent = 0.33
        else:
            percent = self.game_points() / (3.0 * (self.games + (2*self.byes)))
        return max(round(percent, 2), 0.33)

    def opponent_match_win_percentage(self):
        if self.matches == 0: return 0.33
        percentage = [o.match_win_percentage() for o in self.past_opponents]
        return round(sum(percentage) / len(percentage), 2)

    def opponent_game_win_percentage(self):
        if self.games == 0: return 0.33
        percentage = [o.game_win_percentage() for o in self.past_opponents]
        return round(sum(percentage) / len(percentage), 2)

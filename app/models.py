from app import app, db


class User(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(128), index=True)
    tournaments = db.relationship('Tournament', backref='user', lazy='dynamic',
                                  cascade='all, delete-orphan')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_admin(self):
        return self.id in app.config["ADMIN_USERS"]

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User {}>'.format(self.id)


# Each tournament contains a list of players and a number of rounds.
class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    players = db.relationship('Player', backref='tournament', lazy='dynamic',
                              cascade='all, delete-orphan')
    rounds = db.relationship('Round', backref='tournament', lazy='dynamic',
                             cascade='all, delete-orphan')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Tournament {}>'.format(self.name)

    def current_round(self):
        if not self.rounds.all(): return None

        round_number = max([r.round_number for r in self.rounds])
        return [r for r in self.rounds if r.round_number == round_number][0]

    def active_players(self):
        return [p for p in self.players if p.active]

    def seated(self):
        # At least one active player has a seat assigned to them.
        return True in [p.seated() for p in self.active_players()]

    def paired(self):
        # At least one active player has an opponent.
        return True in [p.paired() for p in self.active_players()]


# Each round contains a number of matches.
class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    round_number = db.Column(db.Integer)
    matches = db.relationship('Match', backref='round', lazy='dynamic',
                              cascade='all, delete-orphan')

    __table_args__ = (db.UniqueConstraint('tournament_id', 'round_number',
                      name='_tournament_round_uc'),)

    def __repr__(self):
        return '<Round {}>'.format(self.round_number)

    def reporting_begun(self):
        # At least match in the round has reported.
        return True in [m.reported() for m in self.matches]

    def reporting_complete(self):
        # All matches in the round have reported.
        return not False in [m.reported() for m in self.matches]


# Each match has two players (seats), a table number, and win/loss information.
class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    round_id = db.Column(db.Integer, db.ForeignKey('round.id'))
    table_number = db.Column(db.Integer)
    draws = db.Column(db.Integer, default=0)
    seat_1 = db.relationship('Player', backref='matches_1',
                             foreign_keys='[Match.seat_1_id]')
    seat_2 = db.relationship('Player', backref='matches_2',
                             foreign_keys='[Match.seat_2_id]')
    seat_1_wins = db.Column(db.Integer, default=0)
    seat_2_wins = db.Column(db.Integer, default=0)
    seat_1_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    seat_2_id = db.Column(db.Integer, db.ForeignKey('player.id'))

    __table_args__ = (db.UniqueConstraint('round_id', 'table_number',
                      name='_round_table_uc'),)

    def __init__(self, seat_1, seat_2, table_number, seat_1_wins=0,
                 seat_2_wins=0, draws=0):
        self.seat_1 = seat_1
        self.seat_2 = seat_2
        self.table_number = table_number
        self.draws = draws
        self.seat_1_wins = seat_1_wins
        self.seat_2_wins = seat_2_wins

    def __repr__(self):
        return '<Match {}>'.format(self.table_number)

    def games(self):
        return self.seat_1_wins + self.seat_2_wins + self.draws

    def reported(self):
        return self.games() != 0

    def winner(self):
        if self.seat_1_wins > self.seat_2_wins:
            return self.seat_1
        elif self.seat_2_wins > self.seat_1_wins:
            return self.seat_2
        else:
            return None

    def is_bye(self):
        return self.seat_1 is None or self.seat_2 is None

    def is_draw(self):
        return self.seat_1_wins == self.seat_2_wins and self.games() > 0 

    def wins(self, p):
        if self.seat_1 is p:
            return self.seat_1_wins
        elif self.seat_2 is p:
            return self.seat_2_wins
        else:
            return None

    # When reporting results, if seat_2 is null, we set seat_1_wins to 2.
    # (This is a bye.)


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    active = db.Column(db.Boolean, default=True)
    table = db.Column(db.Integer, default=0)
    seat = db.Column(db.Integer, default=0)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))

    def __repr__(self):
        return '<Player {}>'.format(self.name)

    def current_match(self):
        r = self.tournament.current_round()

        if not r:
            return None

        m = [m for m in r.matches if m.seat_1 is self or m.seat_2 is self]

        if (len(m) != 1):
            return None

        return m[0]

    def matches(self):
        # Matches are stored separately, because you might be seat 1 or 2,
        # which are different columns in the match table. This function fixes
        # that.
        return self.matches_1 + self.matches_2

    def opponent(self):
        m = self.current_match()
        if self.active and m:
            return m.seat_1 if m.seat_2 is self else m.seat_2
        else:
            return None

    def opponents(self):
        return [m.seat_1 if m.seat_2 is self else m.seat_2 for m in
                self.matches()]

    def total_matches(self):
        count = len(self.matches())     # Includes the current match.
        if self.current_match() and not self.current_match().reported():
            count -= 1
        return count

    def total_games(self):
        return sum([m.games() for m in self.matches()])

    def byes(self):
        return len([m for m in self.matches() if m.is_bye()])

    def match_wins(self):
        # Assumes that byes are properly recorded as a 2-game match win.
        return len([m for m in self.matches() if m.winner() is self])

    def game_wins(self):
        # Assumes that byes are properly recorded as a 2-game match win.
        return sum([m.wins(self) for m in self.matches()])

    def match_draws(self):
        return len([m for m in self.matches() if m.is_draw()])

    def game_draws(self):
        return sum([m.draws for m in self.matches()])

    def match_points(self):
        # Assumes that byes are properly recorded as a 2-game match win.
        return (3 * self.match_wins()) + self.match_draws()

    def game_points(self):
        # Assumes that byes are properly recorded as a 2-game match win.
        return (3 * self.game_wins()) + self.game_draws()

    def match_win_percentage(self):
        if self.total_matches() == 0:
            percent = 0.33
        else:
            percent = self.match_points() / (3.0 * self.total_matches())
        return max(round(percent, 2), 0.33)

    def game_win_percentage(self):
        if self.total_games() == 0:
            percent = 0.33
        else:
            percent = self.game_points() / (3.0 * self.total_games())
        return max(round(percent, 2), 0.33)

    def op_match_win_percentage(self):
        # BYES are ignored for opponents' records.
        opponents = [o.match_win_percentage() for o in self.opponents() if o]
        if not opponents:
            return 0.33
        return round(sum(opponents) / len(opponents), 2)

    def op_game_win_percentage(self):
        # BYES are ignored for opponents' records.
        opponents = [o.game_win_percentage() for o in self.opponents() if o]
        if not opponents:
            return 0.33
        return round(sum(opponents) / len(opponents), 2)

    def points(self):
        return self.match_points()

    def tb_1(self):
        return self.op_match_win_percentage()

    def tb_2(self):
        return self.game_win_percentage()

    def tb_3(self):
        return self.op_game_win_percentage()

    def seated(self):
        return self.seat > 0

    def paired(self):
        return self.opponent() is not None


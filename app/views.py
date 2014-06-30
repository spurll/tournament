from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from math import floor, ceil
from random import shuffle
import ldap

from app import app, db, lm
from forms import LoginForm, CreateForm, ReportForm
from models import User, Tournament, Round, Match, Player
from authenticate import authenticate


@app.route('/')
@app.route('/index')
def index():
    return redirect(url_for("list_tournaments"))


@app.route('/tournament/list')
@login_required
def list_tournaments():
    """
    Lists all tournaments for the user and allows the user to create, delete or
    resume one.
    """
    user = g.user
    tournaments = User.query.get(user.id).tournaments.order_by( \
                  Tournament.id.desc())

    if not tournaments:
        flash("You don't have any active tournaments.")

    return render_template("list.html", title="Active Tournaments", user=user,
                           tournaments=tournaments, round=None)


@app.route('/tournament/create', methods=['GET', 'POST'])
@login_required
def create_tournament():
    """
    Gets a list of players, initializes the tournament, sets it as the current
    tournament, then passes control to the tournament main menu.
    """
    form = CreateForm()

    if form.is_submitted():
        print "Create form submitted. Validating..."

        if form.validate_on_submit():
            print "Validated. Creating tournament..."

            tournament = Tournament(name=form.name.data, user_id=g.user.id)

            # Players is a hidden field which contains comma-separated player
            # names. The form contains a text field with an "Add Player" link
            # next to it. When clicked, this will append the player name to the
            # hidden field, and add a static text element to the form with the
            # player's name and a "Drop Player" link next to it.

            players = form.players.data.split("|")
            for player in players:
                p = Player(name=player)
                tournament.players.append(p)
            
            db.session.add(tournament)
            db.session.commit()

            session["tournament"] = tournament.id

            return redirect(url_for('main_menu'))
        else:
            flash("Error: {}".format(form.errors))
            print "Unable to validate."
            print "Errors: {}".format(form.errors)
 
    title = "Create Tournament"
    return render_template("create.html", title=title, user=g.user, form=form,
                           round=None)


@app.route('/tournament/resume', methods=['GET'])
@login_required
def resume_tournament():
    """
    Sets the current tournament to the specified ID and passes control to the
    tournament main menu.
    """
    id = request.args.get("id", "")
    tournament = validate_tournament(id)

    if tournament:
        session["tournament"] = id
        return redirect(url_for("main_menu"))
    else:
        return redirect(url_for("index"))


@app.route('/tournament/delete', methods=['GET'])
@login_required
def delete_tournament():
    """
    Deletes the specified tournament from the DB then returns to the tournament
    list.
    """
    id = request.args.get("id", "")
    tournament = validate_tournament(id)

    if tournament:
        db.session.delete(tournament)
        db.session.commit()

        # Verify that the tournament was deleted.
        if Tournament.query.get(id):
            flash("Error: Unable to delete tournament.")
        else:
            flash("Tournament deleted.")

    return redirect(url_for("index"))


@app.route('/tournament/suspend')
@login_required
def suspend():
    """
    Suspends the tournament and returns control to the tournament list.
    """
    session["tournament"] = None
    return redirect(url_for("index"))


@app.route('/tournament')
@login_required
def main_menu():
    """
    Main menu for the tournament.
    """
    user = g.user
    tournament = g.tournament

    if not tournament:
        return redirect(url_for("list_tournaments"))

    # Pass in booleans for:
    #   seated: players have been seated
    #   paired: players have been paired with opponents
    #   reporting: at least one player (but not all) have reported

    title = tournament.name
    round = tournament.current_round()
    paired = tournament.paired()
    seated = tournament.seated()
    reporting = round.reporting_begun() if round else False
    reported = round.reporting_complete() if round else False

    if round: round = round.round_number

    # Reporting removes opponents (sends to past opponents list).
    # Ensure that once reporting has begun, players' pairings cannot be edited.
    # Add the ability to finish (delete from DB) the tournament at the end.
    # Pop up an are-you-sure? message

    # We need a way to guarantee that whenever a bye match is created, it is
    # initialized with one player and with seat_1_wins initialized to 2.

    return render_template("tournament.html", title=title, user=user,
                           round=round, seated=seated, paired=paired,
                           reporting=reporting, reported=reported)


@app.route('/seat')
@login_required
def seat_players():
    """
    Seating players assigns a seat and table number to them.
    """
    user = g.user
    tournament = g.tournament

    if not tournament:
        return redirect(url_for("list_tournaments"))

    if tournament.seated():
        flash("Players have already been seated.")
        return redirect(url_for("view_seats"))

    active = tournament.active_players()
    shuffle(active)

    table_count = number_of_tables(len(active))
    table_size = int(ceil(float(len(active)) / table_count))

    for t in xrange(table_count):
        for s in xrange(table_size):
            index = (t * table_size) + s
            if index < len(active):
                # Update player objects.
                print "Index: {}".format(index)
                active[index].table = t + 1
                active[index].seat = s + 1
            else:
                break

    db.session.commit()
    return redirect(url_for("view_seats"))


@app.route('/view/seating')
@login_required
def view_seats():
    """
    Displays assigned seating.
    """
    user = g.user
    tournament = g.tournament

    if not tournament:
        return redirect(url_for("list_tournaments"))

    if not tournament.seated():
        return redirect(url_for("seat_players"))

    if tournament.paired():
        return redirect(url_for("view_pairs"))

    active = tournament.active_players()
    tables = []
    for t in set(p.table for p in active):
        table = [p for p in active if p.table == t]
        table.sort(key=lambda p: p.seat)
        tables.append(table)

    title = "Seating"
    return render_template("seating.html", title=title, user=user,
                           tables=tables, round=None)


@app.route('/pair')
@login_required
def pair_players():
    """
    Pairing players adds a round to the tournament and pairs with an opponent.
    Ensure that once reporting has begun, players cannot be re-paired
    (unreported players must either report or drop).
    """
    user = g.user
    tournament = g.tournament

    if not tournament:
        return redirect(url_for("list_tournaments"))

    active = tournament.active_players()

    bye_player = None
    table = 1

    current_round = tournament.current_round()
    first_round = not current_round
    seated = tournament.seated()
    reporting = not first_round and not current_round.reporting_complete()

    if first_round and not seated:
        flash("Unable to pair players. Players must be seated first.")
        return redirect(url_for("main_menu"))

    if reporting:
        flash("Unable to pair players. Results must be reported first.")
        return redirect(url_for("main_menu"))

    # If it's the first round, pair players by seat.
    if first_round:
        # Begin a new round.
        round = Round(round_number=1)
        tournament.rounds.append(round)

        # For each draft table, pair players as far as possible. Then pair any
        # leftover players together between tables. Then, if anyone is left
        # that player gets a bye.

        unpaired = []
        draft_tables = [[p for p in active if p.table == t] for t in
                        {p.table for p in active}]
        for current in draft_tables:
            current.sort(key=lambda p: p.seat)
            player_count = len(current)

            if player_count % 2 != 0:
                # The player in the last seat is not paired at this table.
                unpaired.append(current[player_count - 1])
                player_count -= 1

            # Each player will face an opponent halfway around their table.
            for i in xrange(player_count / 2):
                opponent = current[(i + (player_count / 2)) % player_count]

                match = create_match(current[i], opponent, table)
                round.matches.append(match)
                table += 1

        player_count = len(unpaired)
        # Pair any players that couldn't be paired with their own draft tables.
        if player_count:
            if player_count % 2 != 0:
                # If there is an odd number of players, someone has a bye.
                bye_player = unpaired[player_count - 1]
                player_count -= 1

            for i in xrange(player_count / 2):
                opponent = unpaired[(i + (player_count / 2)) % player_count]

                match = create_match(unpaired[i], opponent, table)
                round.matches.append(match)
                table += 1

            if bye_player:
                # BYE
                match = create_match(bye_player, None, table)
                round.matches.append(match)

    # Pair based upon points.
    else:
        active.sort(key=rank, reverse=True)

        # Begin a new round.
        round = Round(round_number=tournament.current_round().round_number+1)
        tournament.rounds.append(round)

        # We can't just look at player.opponent() to see if they've been paired
        # because this round that we're creating doesn't become the "current
        # round" until it's committed to the DB. Consequently,
        # player.opponent() won't work either. Hence, a list of paired players.
        paired = []

        # Each player faces an opponent not previously faced of similar rank.
        for i in xrange(len(active)):
            if active[i] not in paired:
                for j in xrange(i + 1, len(active)):
                    if active[j] not in paired and \
                            active[j] not in active[i].opponents():
                        print "Pairing {} with {}.".format(active[i], active[j])
                        match = create_match(active[i], active[j], table)
                        round.matches.append(match)
                        table += 1
                        paired.append(active[i])
                        paired.append(active[j])
                        break

                else:
                    if not active[i].opponent():
                        # BYE
                        match = create_match(active[i], None, table)
                        round.matches.append(match)
                        table += 1
            else:
                print "{} already has an opponent.".format(active[i])

    db.session.add(round)
    db.session.commit()

    return redirect(url_for("view_pairs"))


@app.route('/view/pairings')
@login_required
def view_pairs():
    """
    Displays assigned match pairings.
    """
    user = g.user
    tournament = g.tournament

    if not tournament:
        return redirect(url_for("list_tournaments"))

    if not tournament.paired():
        return redirect(url_for("pair_players"))

    title = "Pairings"
    round = tournament.current_round()
    matches = sorted(round.matches, key=lambda m: m.table_number)
    return render_template("pairing.html", title=title, user=user,
                           round=round.round_number, matches=matches)


@app.route('/edit/pairings')
@login_required
def edit_pairings():
    """
    Allows the tournament organizer to edit pairings, because our algorithm
    isn't very good.
    """
    return redirect(url_for('main_menu'))


@app.route('/report')
@login_required
def report_results():
    """
    Displays pairings and allows the tournament organizer to report wins,
    losses, and draws for all matches in the current round.
    """
    user = g.user
    tournament = g.tournament

    if not tournament:
        return redirect(url_for("list_tournaments"))

    if not tournament.seated():
        return redirect(url_for("main_menu"))

    title = "Report Results"
    round = tournament.current_round()
    matches = sorted(round.matches, key=lambda m: m.table_number)
    return render_template("report.html", title=title, user=user,
                           round=round.round_number, matches=matches)


@app.route('/report/match', methods=['GET', 'POST'])
@login_required
def report_match():
    """
    Handles the reporting of a given match.
    """
    user = g.user
    tournament = g.tournament

    if not tournament:
        return redirect(url_for("list_tournaments"))

    if not tournament.seated():
        return redirect(url_for("main_menu"))

    form = ReportForm()
    win, loss, draw = 0, 0, 0

    if form.is_submitted():
        print "Report form submitted. Validating..."
        match = form.match.data

        if form.validate_on_submit():
            print "Validated. Reporting..."
            win = floor(form.seat_1.data)
            loss = floor(form.seat_2.data)
            draw = floor(form.draws.data)
        else:
            flash("Error: {}".format(form.errors))
            print "Unable to validate."
            print "Errors: {}".format(form.errors)
    else:
        match = request.args.get("match")

    print "Match: {}".format(match)
    if match: match = Match.query.get(match)

    round = tournament.current_round()

    if not match or match not in round.matches:
        flash("Unable to report. The specified match is not in this round.")
        return redirect(url_for("main_menu"))

    # BYEs get reported automatically.
    if not match.seat_2:
        win, loss, draw = 2, 0, 0

    # We're doing the actual reporting!
    if win or loss or draw:
        match.seat_1_wins = win if win else 0
        match.seat_2_wins = loss if loss else 0
        match.draws = draw if draw else 0

        db.session.commit()
        return redirect(url_for("report_results"))

    # No results yet. We're requesting that the user reports!
    title = "Results: {} vs. {}".format(match.seat_1.name, match.seat_2.name)
    form.seat_1.label = "Wins for {}".format(match.seat_1.name)
    form.seat_2.label = "Wins for {}".format(match.seat_2.name)
    form.match.data = match.id
    return render_template("match.html", title=title, user=user,
                           round=round.round_number, match=match, form=form)


@app.route('/view/standings')
@login_required
def standings():
    """
    Displays current tournament standings.
    """
    user = g.user
    tournament = g.tournament

    if not tournament:
        return redirect(url_for("list_tournaments"))

    round = tournament.current_round()
    if round:
        round = round.round_number

    title = "Standings"
    players = sorted(tournament.players.all(), key=rank, reverse=True)
    return render_template("standings.html", title=title, user=user,
                           round=round, players=players, close=False)


@app.route('/view/stats')
@login_required
def player_stats():
    """
    Displays detailed player stats.
    """
    user = g.user
    tournament = g.tournament

    if not tournament:
        return redirect(url_for("list_tournaments"))

    if not tournament.current_round():
        return redirect(url_for("main_menu"))

    players = tournament.players
    title = "Detailed Player Statistics"
    round = tournament.current_round().round_number
    return render_template("select.html", title=title, user=user, round=round,
                           players=players, next="player_details")


@app.route('/view/details', methods=['GET'])
@login_required
def player_details():
    """
    Displays detailed stats for a given player.
    """
    user = g.user
    tournament = g.tournament

    if not tournament:
        return redirect(url_for("list_tournaments"))

    if not tournament.current_round():
        return redirect(url_for("main_menu"))

    id = request.args.get("player")
    if id:
        player = [p for p in tournament.players if p.id == int(id)][0]
    else:
        flash("No player specified.")
        return redirect(url_for("player_stats"))

    matches = sorted(player.matches(), key=lambda m: m.round.round_number)

    match_details = []
    for m in matches:
        if m.reported():
            if m.seat_1 is player:
                details = {"opponent": m.seat_2.name if m.seat_2 else None,
                           "result": "Draw",
                           "wins": m.seat_1_wins,
                           "losses": m.seat_2_wins,
                           "draws": m.draws}
            else:
                details = {"opponent": m.seat_1.name if m.seat_1 else None,
                           "result": "Draw",
                           "wins": m.seat_2_wins,
                           "losses": m.seat_1_wins,
                           "draws": m.draws}

            if details["wins"] > details["losses"]:
                details["result"] = "Won!"
            elif details["wins"] < details["losses"]:
                details["result"] = "Lost!"

            match_details.append(details)

    title = "Statistics for {}".format(player.name)
    round = tournament.current_round().round_number
    return render_template("stats.html", title=title, user=user, round=round,
                           player=player, matches=match_details)


@app.route('/drop')
@login_required
def drop_player():
    """
    Drops a player from the tournament.
    """
    user = g.user
    tournament = g.tournament

    if not tournament:
        return redirect(url_for("list_tournaments"))

    id = request.args.get("player")
    if id:
        player = [p for p in tournament.players if p.id == int(id)][0]
        if not player.current_match() or player.current_match().reported():
            flash("{} dropped.".format(player.name))
            player.active = False
            db.session.commit()
        else:
            flash("Unable to drop {}: match results must be reported first."
                  .format(player.name))

    round = tournament.current_round()
    if round:
        round = round.round_number

    players = tournament.active_players()
    title = "Drop Players"
    return render_template("select.html", title=title, user=user, round=round,
                           players=players, next="drop_player")


    # If the player is in a match (that hasn't been reported yet), remove them.
    # (Becomes a BYE.)
    return redirect(url_for('main_menu'))


@app.route('/tournament/close')
@login_required
def close_tournament():
    """
    Displays final stats, then deletes the tournament.
    """
    user = g.user
    tournament = g.tournament

    if not tournament:
        return redirect(url_for("list_tournaments"))

    if not tournament.current_round():
        return redirect(url_for("main_menu"))

    title = "Final Standings"
    round = tournament.current_round().round_number
    players = sorted(tournament.players.all(), key=rank, reverse=True)
    return render_template("standings.html", title=title, user=user,
                           round=round, players=players, close=tournament.id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Logs the user in using LDAP authentication.
    """
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))

    form = LoginForm()

    if request.method == 'GET':
        return render_template('login.html', title="Log In", form=form)

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        try:
            print "Logging in..."
            user = authenticate(username, password)
        except ldap.INVALID_CREDENTIALS:
            user = None

        if not user:
            print "Login failed."
            flash("Login failed.")
            return render_template('login.html', title="Log In", form=form)

        if user and user.is_authenticated():
            db_user = User.query.get(user.id)
            if db_user is None:
                db.session.add(user)
                db.session.commit()

            login_user(user, remember=form.remember.data)

            return redirect(request.args.get('next') or url_for('index'))

    return render_template('login.html', title="Log In", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/tournament/clear')
@login_required
def clear():
    """
    Allows administrators to delete all tournaments from the DB.
    """
    user = g.user
    if user.is_admin():
        clear_tournaments()
    return redirect(url_for('index'))


@lm.user_loader
def load_user(id):
    return User.query.get(id)


@app.before_request
def before_request():
    g.user = current_user
    if "tournament" not in session.keys():
        session["tournament"] = None
    g.tournament = Tournament.query.get(session["tournament"]) \
                   if session["tournament"] else None


def clear_tournaments():
    Tournament.query.delete()
    db.session.commit()


def validate_tournament(id):
    user = g.user

    # Verify that an ID was supplied.
    if id:
        tournament = Tournament.query.get(id)

        # Verify that the ID corresponds to a tournament.
        if tournament:
            # Verify that the tournament is owned by this user.
            if tournament.user == user:
                return tournament
            else:
                flash("You do not have permission to access this tournament.")
        else:
            flash("Error: The specified tournament does not exist.")
    else:
        flash("Error: No tournament specified.")

    return None


def number_of_tables(player_count):
    """
    Players should be seated such that tables have as close to eight players
    each as possible.
    """
    target = app.config["IDEAL_TABLE"]
    possible_tables = range(1, player_count + 1)
    diff = [abs(floor(player_count / i) - target) for i in possible_tables]
    return int(diff.index(min(diff))) + 1


def create_match(player, opponent, table_number):
    """
    Creates a match object with the two specified players.
    """
    match = Match(seat_1=player, seat_2=opponent, table_number=table_number)

    player.seat = 1
    player.table = table_number

    if opponent:
        opponent.seat = 2
        opponent.table = table_number

    return match


def rank(p):
    """
    A key function that allows players to be sorted in rank order.
    """

    # Example: 12 points, with tie-breakers of 0.33, 1.00, and 0.90 becomes...
    rank = p.points()               # 12.
    rank += p.tb_1() / 10           #    033
    rank += p.tb_2() / 10000        #       100
    rank += p.tb_3() / 10000000     #          090
    return rank                     # 12.03310009


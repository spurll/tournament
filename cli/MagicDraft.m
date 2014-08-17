% Known Bugs:
%
%     Tiebreakers don't work properly! Aron faced Nick in round two. Nick
%     had a bye. Aron lost to Nick, who won 2-0. Aron's first tiebreaker
%     (Nick's match win percentage) was 1.25. Derp?
%
%     See function "PairPlayers".

function MagicDraft
	global player;

	playerNames = { 'Gem'
					'Curt'
					'Matt'
					'Aron'
					'Brendan'
					'Mike'
					'Dustin'
					'Bhavek'
					'Nick'
					'Cozmin'
					'Eric'
				  };

	rand( 'twister', sum( 100 * clock ) );

	player = struct;
	for i = 1:numel( playerNames )
		player( i ).name = playerNames{ i };
		player( i ).points = 0;
		player( i ).gamePoints = 0;
		player( i ).gamesPlayed = 0;
		player( i ).opponent = '';
		player( i ).pastOpponents = {};
		player( i ).active = true;
		player( i ).reported = false;
	end

	while true
		clc;
		Table( 'Current Players', { player( [ player.active ] ).name } );
		fprintf( '\n' );
		selection = strrep( Menu( 'Would you like to add or drop players?', 'No', 'Drop Player', 'Add Player' ), ' ', '' );
		clc;
		switch selection
			case 'No'
				break;
			otherwise
				feval( selection );
		end
	end

	while true;
		clc;
		selection = strrep( Menu( 'Main Menu', 'Seat Players', 'Pair Players', 'Edit Pairings', 'Drop Player', 'Report Results', 'Standings', 'Exit' ), ' ', '' );
		clc;
		switch selection
			case 'Exit'
				fprintf( '\nGoodbye!\n' );
				pause( 1 );
				clc;
				return;
			otherwise
				feval( selection );
		end
	end
end

function DropPlayer
	global player;

	while true
		clc;
		playerNames = { player( [ player.active ] ).name };
		drop = Menu( 'Select a player to drop.', playerNames{ : }, '', 'None' );
		clc;
		if strcmp( drop, 'None' ), break; end
		player( strmatch( drop, { player.name } ) ).active = false;
	end
end

function AddPlayer
	global player;

	fprintf( '\nPlease enter the new player''s name below:\n' );
	playerName = input( '>> ', 's' );
	player( end + 1 ) = struct( 'name', playerName, 'points', 0, 'gamePoints', 0, 'gamesPlayed', 0, 'opponent', [], 'pastOpponents', {{}}, 'active', true, 'reported', false );
end

function SeatPlayers
	global player;

	active = player( [ player.active ] );
	inactive = player( ~[ player.active ] );
	seat = randperm( numel( active ) );
	player = [ active( seat ) inactive ];

	clc;
	Table( 'Seat', 1:numel( active ), 'Player', { active( seat ).name } );
	pause;
end

function EditPairings
	global player;

	numPlayers = sum( [ player.active ] );
	seats = 1:numPlayers;

	while true
		activePlayers = player( [ player.active ] );
		activeNames = { activePlayers.name };

		clc;
		Table( 'Player', { activePlayers.name }, 'Opponent', { activePlayers.opponent } );
		fprintf( '\n' );

		player1 = Menu( 'Select a Player', activeNames{ : }, '', 'Cancel', true );
		if player1 ~= numel( activeNames ) + 1
			fprintf( '\n' );
			player2 = Menu( [ 'Select an Opponent for ' activePlayers( player1 ).name ], activeNames{ seats ~= player1 }, '', 'Cancel', true );

			if player2 >= player1, player2 = player2 + 1; end	% Compensate for the fact that the second list is shorter than the first, which changes the indexing.

			if player2 ~= numel( activeNames ) + 1
				opponent1 = activePlayers( player1 ).opponent;
				opponent2 = activePlayers( player2 ).opponent;

				player( strmatch( activePlayers( player1 ).name, { player.name }, 'exact' ) ).opponent = activePlayers( player2 ).name;
				player( strmatch( activePlayers( player2 ).name, { player.name }, 'exact' ) ).opponent = activePlayers( player1 ).name;

				if ~isempty( opponent1 ), player( strmatch( opponent1, { player.name }, 'exact' ) ).opponent = opponent2; end
				if ~isempty( opponent2 ), player( strmatch( opponent2, { player.name }, 'exact' ) ).opponent = opponent1; end

				fprintf( '%s is now playing %s.\n', activePlayers( player1 ).name, activePlayers( player2 ).name );

				if ~isempty( opponent1 ) && ~isempty( opponent2 )
					fprintf( 'As a result, %s is now playing %s.\n', opponent1, opponent2 );
				elseif ~isempty( opponent1 ) && isempty( opponent2 )
					fprintf( 'As a result, %s now has a bye.\n', opponent1 );
				elseif ~isempty( opponent2 ) && isempty( opponent1 )
					fprintf( 'As a result, %s now has a bye.\n', opponent2 );
				end
				pause( 3 );
			else
				fprintf( '\nCancelled.\n' );
				pause( 1 );
				return;
			end
		else
			fprintf( '\nCancelled.\n' );
			pause( 1 );
			return;
		end
	end
end

% Known Bugs:
%
%   Pairings can result in multiple byes if bottom-rung players have
%   already played each other.
%
%   Players can hypothetically achieve multiple byes (only if they suck).
%
%   Pairings are not re-randomized each round.

function PairPlayers
	global player;

	numPlayers = sum( [ player.active ] );
	seats = 1:numPlayers;
	activeNames = { player.name };

	% Warn if some players have not reported but least one player has reported.
	if any( [ player.active ] & ~[ player.reported ] ) && any( [ player.active ] & [ player.reported ] )
		clc;
		switch( Menu( 'Reporting is incomplete! Are you sure that you want to re-pair?', 'Yes', 'No' ) )
			case 'No'
				fprintf( '\nCancelled.\n' );
				pause( 1 );
				return;
		end
		clc;
	end

	for i = 1:numel( player )
		player( i ).reported = false;
	end

	if sum( [ player( [ player.active ] ).points ] ) == 0
		if mod( sum( [ player.active ] ), 2 ) ~= 0
			numPlayers = numPlayers - 1;
			player( seats == numel( seats ) ).opponent = '';
		end

		opponent = mod( ( 1:numPlayers ) - 1 + floor( numPlayers / 2 ), numPlayers ) + 1;
		for i = 1:numPlayers
			player( seats( i ) ).opponent = activeNames{ opponent( i ) };
		end
	else
		[ ignore perm ] = sort( [ player.points ], 2, 'descend' );
		player = player( perm );

		for i = 1:numel( player )
			for j = ( i + 1 ):numel( player )
				if player( i ).active && player( j ).active && isempty( player( i ).opponent ) && isempty( player( j ).opponent ) && isempty( strmatch( player( i ).name, player( j ).pastOpponents ) );
					player( i ).opponent = player( j ).name;
					player( j ).opponent = player( i ).name;
					break;
				end
			end
		end
	end

	clc;
	Table( 'Pairings', 'Player', { player( seats ).name }, 'Opponent', { player( seats ).opponent } );
	pause;
end

function ReportResults
	global player;

	results = { [ 2 1 0 ]
				[ 1 2 0 ]
				[ 2 0 0 ]
				[ 0 2 0 ]
				[ 1 0 0 ]
				[ 0 1 0 ]
				[ 1 1 0 ]
				[ 2 0 1 ]
				[ 0 2 1 ]
				[ 1 0 1 ]
				[ 0 1 1 ]
				[ 1 1 1 ]
				[ 0 0 1 ] };

	while any( [ player.active ] & ~[ player.reported ] )
		opponent = [];
		pairings = struct( [] );
		index = 1;

		for i = 1:numel( player )
			if isempty( player( i ).opponent ) && player( i ).active && ~player( i ).reported
				player( i ).reported = true;
				player( i ).points = player( i ).points + 3;
			elseif ~any( opponent == i ) && player( i ).active && ~player( i ).reported
				opponent( index ) = strmatch( player( i ).opponent, { player.name }, 'exact' );

				pairings( index ).left = player( i ).name;
				pairings( index ).right = player( i ).opponent;
				pairings( index ).leftIndex = i;
				pairings( index ).rightIndex = opponent( index );
				pairings( index ).title = [ pairings( index ).left ' versus ' pairings( index ).right ];

				index = index + 1;
			end
		end

		if isempty( pairings )
			fprintf( '\nPlayers must be seated and paired.\n' );
			pause( 1 );
			return;
		else
			clc;
			options = { pairings.title };
			selection = Menu( 'Report Match Results', options{ : }, '', 'Cancel', true );
			if selection == numel( options ) + 1
				fprintf( '\nCancelled.\n' );
				pause( 1 );
				return;
			else
				clc;
				resultMenu = arrayfun( @( x )( sprintf( [ pairings( selection ).left ': %i, ' pairings( selection ).right ': %i, Tie: %i' ], x{ : } ) ), results, 'UniformOutput', false );
				result = results{ Menu( [ 'Game Results: ' options{ selection } ], resultMenu{ : }, true ) };
				clc;

				% Record games played.
				player( pairings( selection ).leftIndex ).gamesPlayed = player( pairings( selection ).leftIndex ).gamesPlayed + sum( result );
				player( pairings( selection ).rightIndex ).gamesPlayed = player( pairings( selection ).rightIndex ).gamesPlayed + sum( result );

				% Record game points.
				player( pairings( selection ).leftIndex ).gamePoints = player( pairings( selection ).leftIndex ).gamePoints + result( 1 ) * 3 + result( 3 );
				player( pairings( selection ).rightIndex ).gamePoints = player( pairings( selection ).rightIndex ).gamePoints + result( 2 ) * 3 + result( 3 );

				% Record match points.
				if result( 1 ) > result( 2 )
					player( pairings( selection ).leftIndex ).points = player( pairings( selection ).leftIndex ).points + 3;
				elseif result( 1 ) < result( 2 )
					player( pairings( selection ).rightIndex ).points = player( pairings( selection ).rightIndex ).points + 3;
				else
					player( pairings( selection ).leftIndex ).points = player( pairings( selection ).leftIndex ).points + 1;
					player( pairings( selection ).rightIndex ).points = player( pairings( selection ).rightIndex ).points + 1;
				end

				% Players have been reported.
				player( pairings( selection ).leftIndex ).reported = true;
				player( pairings( selection ).rightIndex ).reported = true;

				% Add opponents to the list of past opponents.
				player( pairings( selection ).leftIndex ).pastOpponents = [ player( pairings( selection ).leftIndex ).pastOpponents player( pairings( selection ).leftIndex ).opponent ];
				player( pairings( selection ).rightIndex ).pastOpponents = [ player( pairings( selection ).rightIndex ).pastOpponents player( pairings( selection ).rightIndex ).opponent ];
				player( pairings( selection ).leftIndex ).opponent = '';
				player( pairings( selection ).rightIndex ).opponent = '';
			end
		end
	end
	fprintf( '\nAll players have reported.\n' );
	pause( 1 );
end

function Standings
	global player;

	opponentMap = cell( size( player ) );
	matchesPlayed = NaN( size( player ) );
	for i = 1:numel( player )
		opponents = [ player( i ).pastOpponents ];
		matchesPlayed( i ) = numel( opponents );
		for j = 1:numel( opponents )
			opponentMap{ i } = [ opponentMap{ i } strmatch( opponents{ j }, { player.name } ) ];
		end
	end

	matchWin = [ player.points ] ./ ( matchesPlayed .* 3 );
	opponentMatchWin = arrayfun( @( opponents )( mean( matchWin( opponents{ : } ) ) ), opponentMap );
	gameWin = [ player.gamePoints ] ./ ( [ player.gamesPlayed ] .* 3 );
	opponentGameWin = arrayfun( @( opponents )( mean( gameWin( opponents{ : } ) ) ), opponentMap );

	% The minimum value for match-win and game-win percentages is 0.33.
	opponentMatchWin = max( opponentMatchWin, 1 / 3 );
	gameWin = max( gameWin, 1 / 3 );
	opponentGameWin = max( opponentGameWin, 1 / 3 );

	% Sort.
	perm = MultiSort( [ player.points ], opponentMatchWin, gameWin, opponentGameWin, 'descend' );
	names = { player( perm ).name };
	points = [ player( perm ).points ];
	dropped = ~[ player( perm ).active ];
	matchWin = matchWin( perm );
	opponentMatchWin = opponentMatchWin( perm );
	gameWin = gameWin( perm );
	opponentGameWin = opponentGameWin( perm );

	rank = 1:numel( points );
	for i = 2:numel( points );
		if ( points( i ) == points( i - 1 ) ) && ( opponentMatchWin( i ) == opponentMatchWin( i - 1 ) ) && ( gameWin( i ) == gameWin( i - 1 ) ) && ( opponentGameWin( i ) == opponentGameWin( i - 1 ) )
			rank( i ) = rank( i - 1 );
		end
	end

	clc;
	Table( 'Standings', 'Rank', rank, 'Player', names, 'Points', points, ' ', dropped, 'TB 1', opponentMatchWin, 'TB 2', gameWin, 'TB 3', opponentGameWin );
	pause;
end

function permutation = MultiSort( varargin )
	mode = 'ascend';
	if ischar( varargin{ end } ) && ( strcmp( varargin{ end }, 'ascend' ) || strcmp( varargin{ end }, 'descend' ) )
		mode = varargin{ end };
		varargin = varargin( 1:( end - 1 ) );
	end

	[ ignore dim ] = max( size( varargin{ 1 } ) );

	for i = numel( varargin ):-1:1
		[ ignore perm( i, : ) ] = sort( varargin{ i }, dim, mode );
		for j = 1:numel( varargin )
			varargin{ j } = varargin{ j }( perm( i, : ) );
		end
	end

	permutation = perm( end, : );
	for i = ( size( perm, 1 ) - 1 ):-1:1
		permutation = permutation( perm( i, : ) );
	end
end
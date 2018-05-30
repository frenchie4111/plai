from abc import ABCMeta, abstractmethod

import numpy as np
import gym

class RuleSet():
    __metaclass__ = ABCMeta

    def __init__( self, action_space, observation_space, player_count=2 ):
        self.action_space = action_space
        self.observation_space = observation_space
        self.player_count = player_count

    def isValidAction( self, obs, action ):
        """
        Returns True or False if you are allowed to know if this
        is a valid action (or can tell from the obs). Otherwise
        returns None
        """
        return None

    @abstractmethod
    def getIntialState( self ):
        pass

    @abstractmethod    
    def getWinners( self, state ):
        """
        Return winner ids as array or None
        """
        pass

    @abstractmethod
    def turn( self, state, action ):
        """
        Takes a players turn. Does
        nothing to track winner/loser.
        Returns ( bool, obs )
            Bool represents if the move was valid
            tate represents the new game obs
        """
        pass

    @abstractmethod
    def getObservationForPlayer( self, player_id, state ):
        pass

    def invalidAction( self, state ):
        return False, state

class TicTacToeRuleSet( RuleSet ):
    def __init__( self ):
        super( TicTacToeRuleSet, self ).__init__(
            action_space=gym.spaces.Discrete( 9 ),
            observation_space=gym.spaces.Box( low=-1, high=1, shape=( 3, 3 ), dtype=np.int8 ),
            player_count=2
        )

    def isValidAction( self, obs, action ):
        return obs.flatten()[ action ] == 0

    def getIntialState( self ):
        return np.zeros( self.observation_space.shape, dtype=self.observation_space.dtype )

    def getWinners( self, state ):
        board = state.flatten()

        winning_positions = [
            # horizontal
            [ 0, 1, 2 ], # < Heh, this is actually a 2d representation of the board
            [ 3, 4, 5 ],
            [ 6, 7, 8 ],
            # vertical
            [ 0, 3, 6 ],
            [ 1, 4, 7 ],
            [ 2, 5, 8 ],
            # diagonal
            [ 0, 4, 8 ],
            [ 2, 4, 6 ]
        ]

        for winning_position in winning_positions:
            if( board[ winning_position[ 0 ] ] == board[ winning_position[ 1 ] ] == board[ winning_position[ 2 ] ] != 0 ):
                return [ board[ winning_position[ 0 ] ] ]

        if len( board[ board == 0 ] ) == 0: # No more moves, tie
            return np.unique( board )

        return None

    def step( self, player_id, board, action ):
        board = board.copy().flatten()

        if not self.action_space.contains( action ):
            return self.invalidAction( board )

        if board[ action ] != 0:
            return self.invalidAction( board )

        board[ action ] = player_id

        board = board.reshape( self.observation_space.shape )
        return True, board

    def getObservationForPlayer( self, player_id, state ):
        player_moves = state == player_id 
        not_player_moves = np.logical_and( state != player_id, state != 0 )

        obs = np.zeros( state.shape )
        obs[ player_moves ] = 1
        obs[ not_player_moves ] = -1

        return obs

rulesets = {
    'tictactoe': TicTacToeRuleSet()
}

class Game():
    players = []

    def __init__( self, ruleset, on_complete=None ):
        self.ruleset = ruleset
        self.on_complete = on_complete

    def addPlayer( self, player, player_id=None ):
        if player_id is None:
            player_id = len( self.players ) + 1

        player.setRuleset( self.ruleset )
        self.players.append( ( player_id, player ) ) # Players is ( player_id, player instance )

        if len( self.players ) == self.ruleset.player_count:
            return True

        return False

    def notifyGameOver( self, winners ):
        for player_id, player in self.players:
            player.gameOver( player_id in winners, len( winners ) > 1 )
        if self.on_complete is not None:
            self.on_complete( self )

    def notifyAction( self, state, action ):
        for player_id, player in self.players:
            obs = self.ruleset.getObservationForPlayer( player_id, state )
            player.onMove( action, obs )

    def play( self ):
        state = self.ruleset.getIntialState()

        self.notifyAction( state, None )

        running = True
        current_player_i = np.random.randint( 0, len( self.players ) )
        while running:
            current_player_id, current_player = self.players[ current_player_i ]
            print( 'Current_player', current_player_id )

            obs = self.ruleset.getObservationForPlayer( current_player_id, state )
            action = current_player.move( obs )
            print( '\t', action )

            valid, state = self.ruleset.step( current_player_id, state, action )
            print( '\t new state' )
            print( state )

            if not valid:
                pass # disqualify

            self.notifyAction( state, ( current_player_id, action ) )

            winners = self.ruleset.getWinners( state )
            if winners is not None:
                running = False
                print( winners, len( winners ) )
                self.notifyGameOver( winners )

            current_player_i += 1
            current_player_i %= len( self.players )

class AsyncGame( Game ):
    def addPlayer( self, player ):
        super().addPlayer( player )
        player.game = self # Give the player a game instance so they can call move()

    def play( self ):
        self.state = self.ruleset.getIntialState()
        self._current_player_i = np.random.randint( 0, len( self.players ) )
        self.requestNextMove()

    def requestNextMove( self ):
        current_player_id, current_player = self.players[ self._current_player_i ]
        print( self.state )
        obs = self.ruleset.getObservationForPlayer( current_player_id, self.state )
        print( obs )
        action = current_player.move( obs )
        if action is not None:
            self.move( current_player, action )

    def move( self, player, action ):
        current_player_id, current_player = self.players[ self._current_player_i ]

        if player != current_player:
            pass # disqualify

        valid, self.state = self.ruleset.step( current_player_id, self.state, action )

        if not valid:
            player_ids = np.array( [ player_info[ 0 ] for player_info in self.players ] )
            winners = player_ids[ player_ids != current_player_id ]
            self.notifyGameOver( winners )

        self.notifyAction( self.state, ( current_player_id, action ) )

        winners = self.ruleset.getWinners( self.state )
        if winners is not None:
            self.notifyGameOver( winners )
        else:
            self._current_player_i += 1
            self._current_player_i %= len( self.players )
            self.requestNextMove()
   

class AbstractRoom():
    __metaclass__ = ABCMeta

    @abstractmethod
    def join( self, player ):
        pass

class Room( AbstractRoom ):
    # Currently only plays a single instance of a game
    ## TODO: Allow this to run more than one instance of a game
    ## TODO: Figure out how to abstract matchmaking

    def __init__( self, ruleset ):
        self.ruleset = ruleset
        self.game = None

    def join( self, player ):
        if self.game is None:
            self.game = AsyncGame( self.ruleset, on_complete=self.gameComplete )

        start = self.game.addPlayer( player )

        if start:
            self.game.play()

    def gameComplete( self, game ):
        # TODO: Handle game over better
        self.game.play()

class Player():
    __metaclass__ = ABCMeta

    room = None

    def setRuleset( self, ruleset ):
        self.ruleset = ruleset

    def join( self, room ):
        room.join( self )

    def gameOver( self, winner, tie=False ):
        pass

    def onMove( self, action, obs ):
        pass

    @abstractmethod
    def move( self, obs ):
        pass

class RandomPlayer( Player ):
    def gameOver( self, winner, tie=False ):
        if winner:
            print( 'I won' )

    def move( self, obs ):
        action = self.ruleset.action_space.sample()
        while not self.ruleset.isValidAction( obs, action ):
            action = self.ruleset.action_space.sample()
        return action

if __name__ == '__main__':
    room = Room( rulesets[ 'tictactoe' ] )

    player_1 = RandomPlayer()
    player_1.join( room )

    player_2 = RandomPlayer()
    player_2.join( room )


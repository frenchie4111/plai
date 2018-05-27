from abc import ABCMeta, abstractmethod

import numpy as np
import gym

class RuleSet():
    __metaclass__ = ABCMeta

    @abstractmethod
    def getPlayerCount( self ):
        pass

    @abstractmethod
    def getActionSpace( self ):
        pass

    @abstractmethod
    def getObservationSpace( self ):
        pass

    @abstractmethod
    def isValidAction( self, action ):
        pass

class TicTacToeRuleSet( RuleSet ):
    board = np.zeros( ( 9 ) )

    def getPlayerCount( self ):
        return 2

    def getActionSpace( self ):
        return gym.spaces.Discrete( 9 )

    def getObservationSpace( self ):
        return gym.spaces.Box( low=-1, high=1, shape=( 3, 3 ) )

    def isValidAction( self, action ):
        

class Game():
    players = []

    addPlayer( self, player ):
        self.players.append( player )


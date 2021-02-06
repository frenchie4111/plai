import asynchat
import asyncore
import socket
from abc import ABCMeta, abstractmethod
import time
from threading import Timer

import numpy as np

from plai.base import Room, rulesets, Player, RandomPlayer, AsyncGame
from plai.network_client import NetworkClient, makeCommand

connection_map = {}

class MatchMaking():
    players = []

    def __init__( self, gamename ):
        self.gamename = gamename
        self.ruleset = rulesets[ gamename ]

        self.short_timer = None
        self.long_timer = None

    def addPlayer( self, player ):
        self.players.append( player )

        if len( self.players ) >= self.ruleset.player_count:
            print( 'Enough players have joine to start matchmaking' )
            if self.short_timer is None:
                self.short_timer = Timer( 1.0, self.startGame )
                self.short_timer.start()

        if self.long_timer is None:
            self.long_timer = Timer( 5.0, self.startGame )
            self.long_timer.start()

    def startGame( self ):
        print( 'startGame' )

        if self.short_timer is not None:
            self.short_timer.cancel()
        if self.long_timer is not None:
            self.long_timer.cancel()

        print( self.players )

        game_placements = [[]]

        for player in self.players:
            game_placement = game_placements[ -1 ]
            if len( game_placement ) >= self.ruleset.player_count:
                game_placement = []
                game_placements.append( game_placement )
            game_placement.append( player )

        print( game_placements )

        while len( game_placements[ -1 ] ) < self.ruleset.player_count:
            game_placements[ -1 ].append( RandomPlayer() )

        print( game_placements )
        for game_placement in game_placements:
            game = AsyncGame( ruleset=self.ruleset )
            for player in game_placement:
                game.addPlayer( player )
            game.play()
            self.long_timer = Timer( 5.0, self.startGame )
            self.long_timer.start()


matchmaking = {}
for gamename in rulesets.keys():
    matchmaking[ gamename ] = MatchMaking( gamename=gamename )

class RoomServer( asyncore.dispatcher ):
    room = None

    def __init__( self, host, port ):
        asyncore.dispatcher.__init__( self, map=connection_map )
        self.create_socket( socket.AF_INET, socket.SOCK_STREAM )
        self.set_reuse_addr()
        self.bind( ( host, port ) )
        self.listen( 5 )

    def handle_accept( self ):
        pair = self.accept()

        if pair is not None:
            sock, addr = pair
            print( 'Incoming connection from %s' % repr( addr ) )
            player = PlayerHandler( sock, connection_map=connection_map )

class PlayerHandler( NetworkClient, Player ):
    def __init__( self, sock, connection_map ):
        # super( PlayerHandler, self ).__init__( sock )
        NetworkClient.__init__( self, sock=sock, connection_map=connection_map )
        self._action = None

    def onCommand( self, command ):
        print( 'onCommand', command )

        if command[ 'name' ] == 'gamename':
            print( self, 'gamename', command[ 'data' ] )
            matchmaking[ command[ 'data' ] ].addPlayer( self )

        if command[ 'name' ] == 'action':
            print( self, 'taking action', int( command[ 'data' ] ) )
            self.game.move( self, int( command[ 'data' ] ) )

    def gameOver( self, *args ):
        self.push( makeCommand( 'gameOver', args ) )
    
    def onMove( self, *args ):
        self.push( makeCommand( 'onMove', args ) )

    def move( self, obs ):
        self.push( makeCommand( 'move', obs ) )

server = RoomServer( '0.0.0.0', 4200 ) 

print( 'Serving on 0.0.0.0:4200' )

try:
    asyncore.loop( map=connection_map )
    print( 'Left loop' )
except KeyboardInterrupt:
    conns = list( connection_map.values() ) # Copy so we can close these

    for conn in conns:
        conn.close()

import asynchat
import asyncore
import socket
from abc import ABCMeta, abstractmethod
import time
import threading

import numpy as np

from base import Room, rulesets, Player, RandomPlayer

from network_client import NetworkClient, makeCommand

connection_map = {}

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

            if self.room is None:
                self.room = Room( rulesets[ 'tictactoe' ] )
                # random_player = RandomPlayer()
                # random_player.join( self.room )

            player.join( self.room )


class PlayerHandler( NetworkClient, Player ):
    def __init__( self, sock, connection_map ):
        # super( PlayerHandler, self ).__init__( sock )
        NetworkClient.__init__( self, sock=sock, connection_map=connection_map )
        self._action = None

    def onCommand( self, command ):
        print( 'onCommand', command )

        if command[ 'name' ] == 'action':
            print( self, 'taking action', int( command[ 'data' ] ) )
            self.room.game.move( self, int( command[ 'data' ] ) )

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

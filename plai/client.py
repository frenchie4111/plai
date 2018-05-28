import asynchat
import asyncore
import socket
import threading

import pickle

from base import AbstractRoom, Player
import sys
import time

import numpy as np

from network_client import NetworkClient, makeCommand

class RemoteRoomClient( AbstractRoom ):
    def __init__( self, api_key, host='localhost', port=4200 ):
        super( RemoteRoomClient, self ).__init__()

        self.api_key = api_key
        self.host = host
        self.port = port

    def connect( self ):
        self.client = NetworkClient( self.host, self.port )
        self.client.onCommand = self.onCommand
        # self.client.push( makeCommand( 'join' ) )
        print( 'Connected, waiting for game...' )
        asyncore.loop()

    def join( self, player ):
        self.player = player
        self.connect()

    def onCommand( self, command ):
        if command[ 'name' ] == 'move':
            action = player.move( command[ 'data' ] )
            self.client.push( makeCommand( 'action', action ) )

        if command[ 'name' ] == 'gameOver':
            player.gameOver( *command[ 'data' ] )
        
        if command[ 'name' ] == 'onMove':
            player.onMove( *command[ 'data' ] )

class KeyboardPlayer( Player ):
    def printBoard( self, obs ):
        obs = obs.astype( np.int8 )
        for i, row in enumerate( obs ):
            if i:
                print( '------------' )
            print( str( row[ 0 ] ).rjust( 2 ), '|', str( row[ 1 ] ).rjust( 2 ), '|', str( row[ 2 ] ).rjust( 2 ) )

    def move( self, obs ):
        self.printBoard( obs )

        while True:
            action = input( 'Make your move > ' )
            if action == '?':
                print( 'Printing Help:' )
                self.printBoard( np.array( range( 9 ) ).reshape( 3, 3 ) )
                continue
            break

        return int( action )

    def gameOver( self, winner, tie ):
        print( 'Game Over' )
        if tie:
            print( 'Tie!' )
        elif winner:
            print( 'You Win!' )
        else:
            print( 'You Lose :(' )
        print( 'Waiting for next game to start...' )
        

if __name__ == '__main__':
    if len( sys.argv ) != 2:
        print( 'usage: python -m plai.client <api key>' )

    room = RemoteRoomClient( sys.argv[ 1 ] )

    player = KeyboardPlayer()

    player.join( room )

# comm = threading.Thread(target=asyncore.loop)
# comm.daemon = True
# comm.start()
#
# while True:
#     msg = input('> ')
#     client.push( ( msg + '\n' ).encode( 'utf-8' ) )

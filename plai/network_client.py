import asynchat
import asyncore
import socket
import threading
import numpy as np

import pickle

from abc import ABCMeta, abstractmethod

from base import AbstractRoom, Player
import sys
import time

class NetworkClient( asynchat.async_chat ):
    __metaclass__ = ABCMeta

    def __init__( self, sock, port=None, connection_map=None ):
        """
        sock: Either a socet or a hostname
        """
        if port is None:
            asynchat.async_chat.__init__( self, sock=sock, map=connection_map )
        else:
            asynchat.async_chat.__init__( self )
            self.create_socket( socket.AF_INET, socket.SOCK_STREAM )
            self.connect( ( sock, port ) )

        self.terminator = 'TERM'.encode( 'utf-8' )
        self.set_terminator( self.terminator )
        self.buffer = []

    def collect_incoming_data(self, data):
        self.buffer.append( data )
 
    def found_terminator(self):
        bytes = b''.join( self.buffer )
        self.onCommand( pickle.loads( bytes ) )
        self.buffer = []

    def push( self, command ):
        asynchat.async_chat.push( self, pickle.dumps( command ) + self.terminator )

    @abstractmethod
    def onCommand( self, command ):
        pass

def makeCommand( name, data=None ):
    new_command = {
        'name': name,
        'data': data
    }
    return new_command
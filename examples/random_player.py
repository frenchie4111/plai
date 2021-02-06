import sys

from plai.base import RandomPlayer
from plai.client import RemoteRoomClient

host = 'localhost'
if len( sys.argv ) == 2:
    host = sys.argv[ 1 ]

room = RemoteRoomClient( 'example_api_key', host=host )
random_player = RandomPlayer()
random_player.join( room )

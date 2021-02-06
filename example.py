from plai.base import Player
from plai.client import RemoteRoomClient

class CustomPlayer( Player ):
    def move( self, obs ):
        action = self.ruleset.action_space.sample()
        while not self.ruleset.isValidAction( obs, action ):
            action = self.ruleset.action_space.sample()
        return action

room = RemoteRoomClient( 'apikey', host='plai.mikelyons.org' )
player = CustomPlayer()
player.join( room )

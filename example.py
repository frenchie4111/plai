from base import Player

def CustomPlayer( Player ):
    def move( self, obs ):
        action = self.game.ruleset.action_space.sample()
        while not self.game.ruleset.isValidAction( obs, action ):
            action = self.game.ruleset.action_space.sample()
        return action

room = RemoteRoomClient()

while True:
    player = CustomPlayer()
    won = player.join( room )

    if won:
        print( 'I won!' )

import sys
from time import sleep, localtime

from PodSixNet.Server import Server
from PodSixNet.Channel import Channel

BASE_SCORE = 1000

class ClientChannel(Channel):
    """
    This is the server representation of a connected client.
    """
    nickname = "anonymous"
    
    def Close(self):
        self._server.DelPlayer(self)
    
    def Network_init_player(self,data):
        self.nickname = data["nickname"]
        self.color = data["color"]
        self.score = BASE_SCORE
    
    def Network_send_to_opponent(self,data):
        data["who"] = self.opponent
        data["action"] = data["sent_action"]
        new_data = {key:data[key] for key in data if key != "sent_action"}
        self.SendTo(new_data)
        
    def Network_send_to_all(self,data):
        self.SendToAll(data)
        
    def Network_send_to_others(self,data):
        self.SendToOthers(data)

    def Network_new_game_request(self,data):
        """
        data contient : joueur défié et c'est tout
        """
        opponent = data["challenged"]
        self._server.challenge_request(self,opponent)


class MyServer(Server):
    channelClass = ClientChannel
    def __init__(self, mylocaladdr):
        Server.__init__(self, localaddr=mylocaladdr)
        self.players={}
        print('Server launched')
    
    def Connected(self, channel, addr):
        self.AddPlayer(channel)
    
    def AddPlayer(self, player):
        print("New Player connected")
        self.players[player] = True
    
    def PrintPlayers(self):
        print("players' nicknames :",[p.nickname for p in self.players])
  
    def DelPlayer(self, player):
        print("Deleting Player " + player.nickname + " at "+str(player.addr))
        del self.players[player]
       
    def SendToOthers(self, data):
        [p.Send(data) for p in self.players if p.nickname != data["who"]]
    
    def SendToAll(self, data):
        [p.Send(data) for p in self.players]
    
    def SendTo(self, data):
        [p.Send(data) for p in self.players if p.nickname == data["who"]]

    def Launch(self):
        while True:
            self.Pump()
            sleep(0.001)

    def challenge_request(self,challenger,player2_nick):
        player2 = [p for p in self.players if p.nickname == player2_nick][0]
        if self.can_challenge(challenger,player2):
            if self.is_forced_challenge(challenger,player2) :
                player2.opponent = challenger.nickname
                challenger.opponent = player2.nickname
                player2.Send({"action":"forced_challenge"})
                challenger.Send({"action":"forced_challenge"})
            else :
                player2.Send({"action":"challenge","opponent":challenger})
        else :
            challenger.Send({"action":"cannot_challenge","opponent":player2})
    
    def can_challenge(self,challenger,player2):
        return True
    
    def is_forced_challenge(self,challenger,player2):
        return True
        
"""
class Player :
    def __init__(self,idi,nickname,color,score,state):
        self.idi = idi
        self.nickname = nickname
        self.color = color
        self.score = score
        self.state = state
"""   


# get command line argument of server, port
if len(sys.argv) != 2:
    print("Please use: python3", sys.argv[0], "host:port")
    print("e.g., python3", sys.argv[0], "localhost:31425")
    host, port = "localhost","31425"
else:
    host, port = sys.argv[1].split(":")
s = MyServer((host, int(port)))
s.Launch()


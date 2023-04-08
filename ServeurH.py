import sys
from time import sleep, localtime

from PodSixNet.Server import Server
from PodSixNet.Channel import Channel

BASE_SCORE = 1000
WON = 1
LOST = -1

IN_LOBBY = 0
IN_GAME = 1
IN_CHALLENGE = 2


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
        self.state = IN_LOBBY
        self._server.am_i_allowed(self,self.nickname)
    
    def Network_send_to_opponent(self,data):
        data["who"] = self.opponent.nickname
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
        opponent_nick = data["challenged"]
        self._server.challenge_request(self,opponent_nick)

    def Network_challenge_accepted(self,data):
        challenged_nick = data["challenged"]
        opponent = data["opponent"]
        self._server.launch_game(challenged_nick,opponent)
    
    def Network_challenge_denied(self,data):
        self._server.challenge_denied(self,data["opponent"])

    def Network_i_won(self):
        self._server.game_ended(self, WON, self.opponent)

    def Network_i_lost(self):
        self._server.game_ended(self, LOST, self.opponent)

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
        #self.players[player] = True
        player.Send({"action": "initplayer"})
    
    def am_i_allowed(self,player,nickname):
        if nickname not in self.players:
            player.Send({"action":"connexion_accepted"})
            self.players[player] = True
        else :
            player.Send({"action":"connexion_denied"})
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
        challenger.state = IN_CHALLENGE
        player2 = self.get_player(player2_nick)
        if self.can_challenge(challenger,player2):
            if self.is_forced_challenge(challenger,player2) :
                self.launch_game(challenger,player2)
            else :
                player2.Send({"action":"challenge","opponent":challenger})
                player2.state = IN_CHALLENGE
        else :
            challenger.Send({"action":"cannot_challenge","opponent":player2})
    
    def can_challenge(self,challenger,player2):
        """
        prends en compte: l'écart de points ET le fait qu'il soit en game
        """
        
        return abs(challenger.score - player2.score) < 300
            
        
    def is_forced_challenge(self,challenger,player2):
        
        return abs(challenger.score - player2.score) < 200
    
    def launch_game(self,challenger_nick,player2):
        challenger = self.get_player(challenger_nick)
        player2.opponent = challenger
        challenger.opponent = player2
        player2.Send({"action":"launch_game","your_pawn":"UP","opponent_pawn":"DOWN","your_color":player2.color,"opponent_color":challenger.color})
        challenger.Send({"action":"launch_game","your_pawn":"DOWN","opponent_pawn":"UP","your_color":challenger.color,"opponent_color":player2.color})
        player2.state = IN_GAME
        challenger.state = IN_GAME
        
    def challenge_denied(self,challenged,challenger):
        challenger.Send({"action":"challenge_denied","opponent":challenged})
        challenger.state = IN_LOBBY
        challenged.state = IN_LOBBY

    def get_player(self,nick):
        return [p for p in self.players if p.nickname == nick][0]

    def game_ended(self,player,result,opponent):
        self.set_new_score(player,result,opponent)
        player.state = IN_LOBBY
        player.Send({"action":"close_game"})
        
    def set_new_score(self,player,result,opponent):
        old_score = player.score
        opponent_score= opponent.score
        if result == WON :
            player.score = old_score + (100 - (1/3)*(old_score - opponent_score))
        else :
            player.score = old_score - (100 - (1/3)*(old_score - opponent_score))



# get command line argument of server, port
if len(sys.argv) != 2:
    print("Please use: python3", sys.argv[0], "host:port")
    print("e.g., python3", sys.argv[0], "localhost:31425")
    host, port = "localhost","31425"
else:
    host, port = sys.argv[1].split(":")
s = MyServer((host, int(port)))
s.Launch()


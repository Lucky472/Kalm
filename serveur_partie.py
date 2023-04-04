# -*- coding: utf-8 -*-
"""
Created on Mon Apr  3 22:43:23 2023

@author: gadbi
"""

import sys
from time import sleep, localtime

from PodSixNet.Server import Server
from PodSixNet.Channel import Channel

class ClientChannel(Channel):
    """
    This is the server representation of a connected client.
    """
    nickname = "anonymous"
    
    def Close(self):
        self._server.DelPlayer(self)
    
    def Network_temporary(self,data):
        pass

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
        self.listplayers.append()
    
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

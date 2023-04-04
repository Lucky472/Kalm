import sys
from time import sleep
from sys import stdin, exit

from PodSixNet.Connection import connection, ConnectionListener

from tkinter import *
WIDTH=300
HEIGHT=200
R=5

INITIAL=0
ACTIVE=1
DEAD=-1

class Client(ConnectionListener):
    def __init__(self, host, port, window):
        self.window = window
        self.Connect((host, port))

        self.state=INITIAL
        print("Client started")
        print("Ctrl-C to exit")
        print("Enter your nickname: ")
        nickname=stdin.readline().rstrip("\n")
        self.nickname=nickname
        connection.Send({"action": "nickname", "nickname": nickname})
        
    def Network_connected(self, data):
        print("You are now connected to the server")
    
    def Loop(self):
        connection.Pump()
        self.Pump()

    def quit(self):
        self.window.destroy()
        self.state=DEAD
   
    def Network_start(self,data):
        self.state=ACTIVE
        print("started")
   
    def Network_newPoint(self, data):
        (x,y)=data["newPoint"]
        self.window.white_board_canvas.create_oval(x-R,y-R,x+R,y+R)
        self.window.white_board_canvas.update()
    
    def Network_error(self, data):
        print('error:', data['error'][1])
        connection.Close()
    
    def Network_disconnected(self, data):
        print('Server disconnected')
        exit()
    
#########################################################

class ClientWindow(Tk):
    #c'est le view
    def __init__(self, host, port):
        Tk.__init__(self)
        self.client = Client(host, int(port), self)
        self.white_board_canvas = Canvas(self, width=WIDTH, height = HEIGHT,bg='white')
        self.white_board_canvas.pack(side=TOP)
        self.white_board_canvas.bind("<Button-1>",self.drawNewPoint)
        quit_but=Button(self,text='Quitter',command = self.client.quit)
        quit_but.pack(side=BOTTOM)


    def myMainLoop(self):
        while self.client.state!=DEAD:   
            self.update()
            self.client.Loop()
            sleep(0.001)
        exit()    


# get command line argument of client, port
if len(sys.argv) != 2:
    print("Please use: python3", sys.argv[0], "host:port")
    print("e.g., python3", sys.argv[0], "localhost:31425")
    host, port = "localhost", "31425"
else:
    host, port = sys.argv[1].split(":")
client_window = ClientWindow(host, port)
client_window.myMainLoop()




import sys
from time import sleep
from sys import stdin, exit

from PodSixNet.Connection import connection, ConnectionListener

from tkinter import *
from tkinter.colorchooser import askcolor
from tkinter import messagebox as boxedmessage

Y_AXIS_LENGTH = 7
X_AXIS_LENGTH = 7
BOARD_X_LENGTH = 2 * X_AXIS_LENGTH - 1
BOARD_Y_LENGTH = 2 * Y_AXIS_LENGTH - 1
SIZESQUARE = 10
COLORSQUARE = "#A567A3"

HOST, PORT = "localhost", "31425"
NICKNAME = "nick"
BASECOLOR = "#ca7511"

INITIAL=0
ACTIVE=1
DEAD=-1

class Client(ConnectionListener):
    def __init__(self, host, port, window,color,nickname):
        self.window = window
        self.Connect((host, port))
        self.color = color
        self.nickname = nickname
        self.oponent_color = "#f3f300"
        self.state=INITIAL
        print("Client started")
        print("Ctrl-C to exit")

    def Network_initplayer(self,data):
        """
        Envoie les nom et couleur de son joueur
        """
        connection.Send({"action": "nickname", "nickname": self.nickname})
        connection.Send({"action": "color" ,"color": self.color})

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

    def Network_error(self, data):
        print('error:', data['error'][1])
        connection.Close()
    
    def Network_disconnected(self, data):
        print('Server disconnected')
        exit()
    
#########################################################

class ClientWindow(Tk):
    def __init__(self, host, port,color,nickname):
        Tk.__init__(self)
        self.client = Client(host, int(port), self,color,nickname)


    def myMainLoop(self):
        while self.client.state!=DEAD:   
            self.update()
            self.client.Loop()
            sleep(0.001)
        exit()    


class View:
    def __init__(self,window,board):
        self.window = window
        self.canvas_board = Canvas(self.window)
        self.draw_board(board)
    
    def draw_board(self,board):
        for x in range(BOARD_X_LENGTH):
            for y in range (BOARD_Y_LENGTH):
                if self.is_square(x,y):
                    self.canvas_board.create_rectangle(x*SIZESQUARE,y*SIZESQUARE,(x+1)*SIZESQUARE,(y+1)*SIZESQUARE)

    def is_square(self,x,y):
        return (x % 2 == 0) and (y % 2 == 0)


class Model :
    def __init__(self):
        self.board = self.new_board()
        self.pawns = {"UP":Pawn((0, BOARD_X_LENGTH // 2)), "DOWN":Pawn((BOARD_Y_LENGTH, BOARD_X_LENGTH // 2))}
    
    def new_board(self):
        board = [[0 for j in range(BOARD_Y_LENGTH)] for i in range(BOARD_X_LENGTH)]
        for x in range(BOARD_X_LENGTH):
            for y in range (BOARD_Y_LENGTH):
                if self.is_square(x,y):
                    board[x][y] = Square()
                else :
                    board[x][y] = Hole()
        return board
    
    def is_square(self,x,y):
        return (x % 2 == 0) and (y % 2 == 0)
    
    def move_pawn(self,pawn,location):
        pass
    
    def add_wall(self,location,orientation):
        """
        on se contente ici de mettre le mur sans vérifier, ce sera fait au préalable
        """
        x, y = location
        if orientation == "UP":
            self.board[x][y-1].occupied = True
            self.board[x][y].occupied = True
            self.board[x][y+1].occupied = True
        if orientation == "ACROSS":
            self.board[x+1][y].occupied = True
            self.board[x][y].occupied = True
            self.board[x-1][y].occupied = True
    
    def remove_wall(self,location,orientation):
        x, y = location
        if orientation == "UP":
            self.board[x][y-1].occupied = False
            self.board[x][y].occupied = False
            self.board[x][y+1].occupied = False
        if orientation == "ACROSS":
            self.board[x+1][y].occupied = False
            self.board[x][y].occupied = False
            self.board[x-1][y].occupied = False    
    
    def test_add_wall(self,location,orientation):
        x, y = location
        if x == 0 or y == 0 or x == BOARD_X_LENGTH or y == BOARD_Y_LENGTH:
            return False
        if orientation == "UP":
            if self.board[x][y-1].occupied or self.board[x][y].occupied or self.board[x][y+1].occupied :
                return False
        if orientation == "ACROSS":
            if self.board[x-1][y].occupied or self.board[x][y].occupied or self.board[x+1][y].occupied :
                return False
        return self.pathfind_test_with_wall_from(location,orientation)
    
    def accessible_from(self,location,avoid = None):
        x,y = location
        accessible_squares = []
        #aller à gauche
        if x != 0 and not self.board[x-1][y].occupied:
            if not self.board[x-2][y].occupied:
                accessible_squares.append((x-2,y))
            elif (x-2,y) != avoid:
                for square in self.accessible_from((x-2,y),avoid = location):
                    accessible_squares.append(square)
        #aller à droite
        if x != BOARD_X_LENGTH and not self.board[x+1][y].occupied:
            if not self.board[x+2][y].occupied:
                accessible_squares.append((x+2,y))
            elif (x+2,y) != avoid:
                for square in self.accessible_from((x+2,y),avoid = location):
                    accessible_squares.append(square)
        #aller en haut
        if y != 0 and not self.board[x][y-1].occupied:
            if not self.board[x][y-2].occupied:
                accessible_squares.append((x,y-2))
            elif (x,y-2) != avoid:
                for square in self.accessible_from((x,y-2),avoid = location):
                    accessible_squares.append(square)
        #aller en bas
        if y != BOARD_Y_LENGTH and not self.board[x][y+1].occupied:
            if not self.board[x][y+2].occupied:
                accessible_squares.append((x,y+2))
            elif (x,y+2) != avoid:
                for square in self.accessible_from((x,y+2),avoid = location):
                    accessible_squares.append(square)
        return accessible_squares
    
    def pathfind_test_with_wall(self,location,orientation):
        self.add_wall(location, orientation)
        for key,pawn in self.pawns:
            if key == "UP":
                test = self.pathfind_test(pawn.coords, 0)
            else :
                test = self.pathfind_test(pawn.coords, BOARD_Y_LENGTH)
        self.remove_wall(location, orientation)
        return test
    
    def pathfind_test(self,location,targeted_y,all_accessibles=[],new_accessibles=[]):
        if all_accessibles == []:
            acc = list(self.accessible_from(location))
            new_accessibles = acc
            all_accessibles = acc
        else: 
            border = []
            for new_square in new_accessibles:
                for square in self.accessible_from(new_square):
                    if square not in all_accessibles:
                        if square[1] == targeted_y:
                            return True
                        border.append(square)
                        all_accessibles.append(square)
        if border == []:
            return False
        return self.pathfind_test(location,targeted_y,all_accessibles=all_accessibles,new_accessibles=border)


class Pawn :
    def __init__(self,coords):
        self.coords = coords
        
class Hole :
    def __init__(self):
        self.occupied = False
        
class Square :
    def __init__(self):
        self.occupied = False

class Buttons :
    def __init__(self, menu):
        self.menu = menu
        self.frame()
        self.text()
        self.buttons()
        self.entries()
        self.packall()
        
    def frame(self):
        self.frame=Frame(self.menu.Window,bg='#41B77F')
        self.f_pseudo= Frame(self.frame,bg='#41B77F')
        self.f_host = Frame(self.frame,bg='#41B77F')
        self.f_port = Frame(self.frame,bg='#41B77F')
        
    def text(self):
        self.Labeltitle1=Label(self.frame,text='Menu du jeu saucisse',font=("arial",30),bg='#41B77F',fg='white')
        self.Labeltitle2=Label(self.frame,text='Preparez vous à jouer, regarder les règles et choississez votre couleur',font=("arial",10),bg='#41B77F',fg='white')
        self.L_pseudo=Label(self.frame,text='choisi ton pseudo',font=("arial",19),bg='#41B77F',fg='white')
        self.L_host=Label(self.frame,text='host',font=("arial",19),bg='#41B77F',fg='white')
        self.L_port = Label(self.frame,text='port',font=("arial",19),bg='#41B77F',fg='white')

    def buttons(self):
        self.B_quitter=Button(self.menu.Window,text='quitter',command=self.menu.Window.destroy,bg='#ed1111')
        self.B_couleur=Button(self.frame,text='Selectionner une couleur',command=self.menu.change_color,bg='#4065A4')
        self.B_jouer = Button(self.menu.Window,text='   Jouer   ',command= self.menu.open_window,bg='#4065A4')

    def entries(self):
        self.e_pseudo=Entry(self.f_pseudo,font=("arial",20),bg='#41B77F',fg='white')
        self.e_host = Entry(self.f_host,font=("arial",20),bg='#41B77F',fg='white')
        self.e_port = Entry(self.f_port,font=("arial",20),bg='#41B77F',fg='white')
        self.e_pseudo.insert(0,NICKNAME)
        self.e_host.insert(0,HOST)
        self.e_port.insert(0,PORT)

    def packall (self):
        self.frame.pack(expand=YES)
        self.Labeltitle1.pack()
        self.B_quitter.pack(side=LEFT)
        self.Labeltitle2.pack()
        self.B_couleur.pack()
        self.L_pseudo.pack()
        self.e_pseudo.pack()
        self.f_pseudo.pack()
        self.L_host.pack()
        self.f_host.pack()
        self.e_host.pack()
        self.L_port.pack()
        self.e_port.pack()
        self.f_port.pack()
        self.B_jouer.pack(side=BOTTOM)


class Menu :
    def __init__(self):
        self.Window=Tk()
        self.Window.geometry("520x500")
        self.Window.title("menu principal du jeu")
        self.Window.config(background='#41B77F')
        self.buttons = Buttons(self)
        self.color = BASECOLOR
        self.local_server = None
        self.has_defier = False
        self.Window.mainloop()
        
    def open_window(self):
        self.enregistrer_pseudo()
        self.enregistrer_port()
        self.enregistrer_host()
        
        if self.nickname != NICKNAME :
            self.client_window = ClientWindow(self.host, self.port, self.color, self.nickname)
            self.client_window.myMainLoop()
            
        else :
            boxedmessage.showinfo(title=None, message="please change your nickname") 
    
    def change_color(self):
        colors=askcolor(title="Tkinter Color Chooser")
        self.Window.configure(bg=colors[1])
        self.color = colors[1]

    #enregistrer pseudo dans une variable
    def enregistrer_pseudo(self):
        self.nickname=self.buttons.e_pseudo.get()

    def enregistrer_host(self):
        self.host=self.buttons.e_host.get()
        
    def enregistrer_port(self):
        self.port=self.buttons.e_port.get()



# get command line argument of client, port
if len(sys.argv) != 2:
    print("Please use: python3", sys.argv[0], "host:port")
    print("e.g., python3", sys.argv[0], "localhost:31425")
    host, port = "localhost", "31425"
else:
    host, port = sys.argv[1].split(":")


"""client_window = ClientWindow(host, port)
client_window.myMainLoop()
"""

menu = Menu()



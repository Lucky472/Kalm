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
SIZESQUARE = 50
RADIUSPAWN = 17
RADIUSDOTS = 5
COLORDOT = "#EEEEEE"
COLORBOARD = "#454545"
WIDTHWALL = 10
WIDTHLINE = 4
COLORLINE = "#D4D4D4"
COLORWALL = "#AA5372"
LENGTH_LINE = 10
PIXEL_BOARD_X_LENGTH = X_AXIS_LENGTH * SIZESQUARE
PIXEL_BOARD_Y_LENGTH = Y_AXIS_LENGTH * SIZESQUARE
X_OFFSET = 10
Y_OFFSET = 10
SPACING = 4

HOST, PORT = "localhost", "31425"
NICKNAME = "nick"
BASECOLOR = "#ca7511"

INITIAL=0
ACTIVE=1
DEAD=-1
INACTIVE = 2

MOVE_PAWN = 0
PLACE_WALL_UP = 1
PLACE_WALL_ACROSS = 2


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
    
    def Network_placed_wall(self,data):
        self.window.controller.controller_place_wall(data["location"], data["orientation"])
        self.window.controller.set_active()
        
    def Network_moved_pawn(self,data):
        self.window.controller.controller_move_pawn(self.window.controller.opponent_pawn, data["location"])
        self.window.controller.set_active()
        
    def Network_challenge(self,data):
        if self.window.ask_challenge(data["opponent"]):
            self.Send({"action":"challenge_accepted","challenged":self.nickname,"opponent":data["opponent"]})
        else :
            self.Send({"action":"challenge_denied","opponent":data["opponent"]})
    
    def Network_launch_game(self,data):
        self.window.launch_game(data["your_pawn"],data["opponent_pawn"])
    
    def Network_cannot_challenge(self,data):
        """
        indique au joueur que il ne peut pas défier le joueur
        (data["opponent"]) est le joueur ne pouvant pas être défié
        """
        pass
    
    def Network_challenge_denied(self,data):
        self.window.challenge_denied(data["opponent"])
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

    def ask_challenge(self,opponent):
        """
        opponent est l'élément de dico avec tt les attributs du challenger
        demande au joueur si il accepte le défi 
        (si oui, return True
         si non, return False)
        """  

    def send_challenge(self,opponent_nickname):
        """
        fonction appellée par le bouton d'envoi de défi
        """
        self.client.Send({"action":"new_game_request","challenged":opponent_nickname})

    def challenge_denied(opponent):
        """
        opponent est l'élément de dico avec tt les attributs du challenger
        informe le joueur que le challenge a été refusé
        """

    def launch_game(self,my_pawn,opponent_pawn):
        self.controller = Controller(self,self.client,my_pawn,opponent_pawn)

class Controller:
    def __init__(self,window,client,my_pawn,opponent_pawn):
        self.window = window
        self.client = client
        self.model = Model()
        self.view = View(window)
        self.view.canvas_board.bind("<Button-1>",self.board_click)
        self.move = MOVE_PAWN
        self.state = INITIAL
        self.my_pawn = my_pawn
        self.opponent_pawn = opponent_pawn
    
    def set_active(self):
        self.state = ACTIVE
    
    def board_click(self,evt):
        if (self.state == ACTIVE):
            if (self.move == PLACE_WALL_UP): 
                hole = self.detect_clicked_hole(evt.x,evt.y)
                if (hole != None):
                    if self.model.test_add_wall((hole[0],hole[1]),"UP"):
                        self.controller_place_wall((hole[0],hole[1]),"UP")
                        self.send_placed_wall((hole[0],hole[1]),"UP")
            if (self.move == PLACE_WALL_ACROSS): 
                hole = self.detect_clicked_hole(evt.x,evt.y)
                if (hole != None):
                    if self.model.test_add_wall((hole[0],hole[1]),"ACROSS"):
                        self.controller_place_wall((hole[0],hole[1]),"ACROSS")
                        self.send_placed_wall((hole[0],hole[1]),"ACROSS")
            if self.move == MOVE_PAWN :
                square = self.detect_clicked_square(evt.x,evt.y)
                if square != None and square in self.model.accessible_from(self.model.pawns[self.my_pawn]):
                    self.controller_move_pawn(self.my_pawn, square)
                    self.send_moved_pawn(square)

    def controller_move_pawn(self,pawn, location):
        self.view.delete_deletable_dots()
        x,y = location
        self.view.move_pawn(x, y, pawn)
        self.model.move_pawn(pawn, location)
        self.state = INACTIVE
        
    def controller_place_wall(self,location,orientation):
        x,y = location
        self.view.place_wall(x,y,self.move)  
        self.model.add_wall((x,y),orientation)
        self.state = INACTIVE
    
    def detect_clicked_hole(self,pixel_x,pixel_y):
        for x in range(1,X_AXIS_LENGTH):
            x_minus = x*SIZESQUARE + X_OFFSET - LENGTH_LINE
            x_maxus = (x)*SIZESQUARE + X_OFFSET + LENGTH_LINE
            for y in range(1,Y_AXIS_LENGTH):
                y_minus = y*SIZESQUARE + Y_OFFSET - LENGTH_LINE
                y_maxus = (y)*SIZESQUARE + Y_OFFSET + LENGTH_LINE
                if (pixel_x >= x_minus) and (pixel_x <= x_maxus):
                    if (pixel_y >= y_minus) and (pixel_x <= y_maxus):
                        return (x,y)
        return None

    def detect_clicked_square(self,pixel_x,pixel_y):
        for x in range(0,X_AXIS_LENGTH):
            x_minus = x*SIZESQUARE + X_OFFSET + WIDTHLINE
            x_maxus = (x+1)*SIZESQUARE + X_OFFSET - WIDTHLINE
            for y in range(0,Y_AXIS_LENGTH):
                y_minus = y*SIZESQUARE + Y_OFFSET + WIDTHLINE
                y_maxus = (y+1)*SIZESQUARE + Y_OFFSET - WIDTHLINE
                if (pixel_x >= x_minus) and (pixel_x <= x_maxus):
                    if (pixel_y >= y_minus) and (pixel_y <= y_maxus):
                        return (x,y)
    
    def send_placed_wall(self,location,orientation):
        self.client.Send({"action":"send_to_opponent", "sent_action":"placed_wall", "location":location, "orientation":orientation})
    
    def send_moved_pawn(self,location):
        self.client.Send({"action":"send_to_opponent", "sent_action":"moved_pawn", "location":location})

    def set_wall_vertical(self):
        self.view.delete_deletable_dots()
        self.move = PLACE_WALL_UP
                
    def set_wall_horizontal(self):
        self.view.delete_deletable_dots()
        self.move = PLACE_WALL_ACROSS
    
    def set_move_pawn(self):
        self.move = MOVE_PAWN
        x,y = self.model.pawns[self.my_pawn].coords
        self.view.show_plays(x,y)
        
class View:
    def __init__(self,window,color,oponent_color):
        self.window = window
        self.canvas_board = Canvas(self.window,height = PIXEL_BOARD_Y_LENGTH + 2*Y_OFFSET,width =  PIXEL_BOARD_X_LENGTH + 2*X_OFFSET,bg =COLORBOARD )
        self.draw_board()
        self.canvas_.pack()
        # La grille commence à (0,0) donc les coordonnées données vont jusqu'à (6,6) pour une taille de 7 cases
        self.pawns = {"DOWN":self.draw_pawn(X_AXIS_LENGTH // 2,Y_AXIS_LENGTH-1 ),"UP":self.draw_pawn(X_AXIS_LENGTH // 2, 0)}
        self.color = color 
        self.oponent_color = oponent_color
        self.deletable_dots = []

    def draw_board(self):
        #Lignes verticales
        for x in range(X_AXIS_LENGTH+1):
            x01 = SIZESQUARE*x + X_OFFSET +1
            for y in range (Y_AXIS_LENGTH):
                y0 = y*SIZESQUARE + LENGTH_LINE + Y_OFFSET +1
                y1 = (y+1)*SIZESQUARE - LENGTH_LINE + Y_OFFSET +1
                self.canvas_board.create_line(x01,y0,x01,y1,fill = COLORLINE,width=WIDTHLINE)
        #Lignes horizontales
        for y in range(Y_AXIS_LENGTH+1):
            y01 = SIZESQUARE*y + Y_OFFSET +1
            for x in range (X_AXIS_LENGTH):
                x0 = x*SIZESQUARE + LENGTH_LINE + X_OFFSET +1
                x1 = (x+1)*SIZESQUARE - LENGTH_LINE + X_OFFSET +1
                self.canvas_board.create_line(x0,y01,x1,y01,fill = COLORLINE,width=WIDTHLINE)

    def draw_pawn(self,x,y):
        x0,y0 = self.get_center(x,y)
        idd =  self.canvas_board.create_oval(x0 - RADIUSPAWN,y0-RADIUSPAWN,x0 + RADIUSPAWN,y0 + RADIUSPAWN,fill = COLORLINE)
        return idd
    def get_center(self,x,y):
        x0 = x*SIZESQUARE + X_OFFSET + SIZESQUARE//2
        y0 = y*SIZESQUARE + Y_OFFSET + SIZESQUARE//2
        return (x0,y0)

    def delete_pawn(self,pawn_id):
        self.canvas_board.delete(self.pawns.pop(pawn_id))
        
    def move_pawn(self,x,y,pawn_id):
        self.delete_pawn(pawn_id)
        self.pawns[pawn_id] = self.draw_pawn(x,y)
    
    def place_wall(self,x,y,orientation):
            if type == PLACE_WALL_ACROSS:
                self.place_horizontal_wall(x,y)
            elif type == PLACE_WALL_UP:
                self.place_vertical_wall(x,y)

    def show_plays(self,playable_list):
        """
            affiche les points atteignables depuis une position, prend une liste de tuple en argument
        """
        for square in playable_list:
            x0,y0 = self.get_center(square[0],square[1])
            self.deletable_dots.append(self.canvas_board.create_oval(x0 - RADIUSDOTS,y0-RADIUSDOTS,x0 + RADIUSDOTS,y0 + RADIUSDOTS,fill = COLORDOT))

    def delete_deletable_dots(self):
        for i in range(0,len(self.deletable_dots)):
            self.canvas_board.delete(self.deletable_dots.pop(0))

    def place_vertical_wall(self,x,y):
        x0 = x*SIZESQUARE +X_OFFSET + WIDTHLINE
        y0 = y*SIZESQUARE +Y_OFFSET +SPACING
        x1 = x*SIZESQUARE +X_OFFSET - WIDTHLINE
        y1 = (y+2)*SIZESQUARE +Y_OFFSET -SPACING
        self.canvas_board.create_rectangle(x0,y0,x1,y1,fill = COLORWALL)


    def place_horizontal_wall(self,x,y):
        y0 = y*SIZESQUARE +Y_OFFSET + WIDTHLINE
        x0 = x*SIZESQUARE +X_OFFSET +SPACING
        y1 = y*SIZESQUARE +Y_OFFSET - WIDTHLINE
        x1 = (x+2)*SIZESQUARE +X_OFFSET -SPACING
        self.canvas_board.create_rectangle(x0,y0,x1,y1,fill = COLORWALL)
        
class Model :
    def __init__(self):
        self.board = self.new_board()
        self.pawns = {"UP":Pawn((BOARD_X_LENGTH // 2, 0)), "DOWN":Pawn((BOARD_X_LENGTH // 2, BOARD_Y_LENGTH))}
    
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
        pawn_x,pawn_y=self.pawns[pawn].coords
        self.board[pawn_x][pawn_y].occupied = False
        pawn_x,pawn_y=location
        self.pawns[pawn].coords = (pawn_x,pawn_y)
        self.board[pawn_x][pawn_y].occupied = True
        
    
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
        if len(border) == 0:
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
        self.f_liste=Frame(self.frame,bg='#41B77F')
        self.f_adversaire=Frame(self.frame,bg='#41B77F')
        self.f_pseudo= Frame(self.frame,bg='#41B77F')
        self.f_host = Frame(self.frame,bg='#41B77F')
        self.f_port = Frame(self.frame,bg='#41B77F')
        
        
    def text(self):
        self.Labeltitle1=Label(self.frame,text='Menu du jeu quoridor',font=("arial",30),bg='#41B77F',fg='white')
        self.Labeltitle2=Label(self.frame,text='Preparez vous à jouer, regarder les règles et choississez votre couleur',font=("arial",10),bg='#41B77F',fg='white')
        self.L_pseudo=Label(self.frame,text='choisi ton pseudo',font=("arial",19),bg='#41B77F',fg='white')
        self.L_host=Label(self.frame,text='host',font=("arial",19),bg='#41B77F',fg='white')
        self.L_port = Label(self.frame,text='port',font=("arial",19),bg='#41B77F',fg='white')
        self.L_adversaire=Label(self.frame,text='choisis ton adversaire',font=("arial",19),bg='#41B77F',fg='white')

    def afficher_liste_joueur(self,Liste_joueur):
        for i in range(len(Liste_joueur)-2,-1,-2):
            self.L_joueur=Label(self.f_liste,text=Liste_joueur[i]+" "+ str(Liste_joueur[i+1]),font=("arial",10),bg='#4065A4',fg='black',bd=2,relief=SUNKEN)
            self.L_joueur.pack(pady=2)

    def buttons(self):
        self.B_quitter=Button(self.menu.Window,text='quitter',command=self.menu.Window.destroy,bg='#ed1111')
        self.B_couleur=Button(self.frame,text='Selectionner une couleur',command=self.menu.change_color,bg='#4065A4')
        self.B_jouer = Button(self.menu.Window,text='   Jouer   ',command= self.menu.open_window,bg='#4065A4')

    def entries(self):
        self.e_pseudo=Entry(self.f_pseudo,font=("arial",20),bg='#41B77F',fg='white')
        self.e_host = Entry(self.f_host,font=("arial",20),bg='#41B77F',fg='white')
        self.e_port = Entry(self.f_port,font=("arial",20),bg='#41B77F',fg='white')
        self.e_adversaire=Entry(self.f_adversaire,font=("arial",20),bg='#41B77F',fg='white')
        self.e_pseudo.insert(0,NICKNAME)
        self.e_host.insert(0,HOST)
        self.e_port.insert(0,PORT)
        

    def packall (self):
        self.frame.pack(expand=YES)
        self.f_liste.pack(side=RIGHT)
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
        self.L_adversaire.pack()
        self.e_adversaire.pack()
        self.f_adversaire.pack()
        self.B_jouer.pack(side=BOTTOM)
        

class Menu :
    def __init__(self):
        self.Window=Tk()
        self.Window.geometry("520x500")
        self.Window.title("menu principal du jeu")
        self.Window.config(background='#41B77F')
        self.dico_list=[{"name":"matteo","score":2},{"name":"killian","score":13},{"name":"adrien","score":12},{"name":"lucas","score":4}]
        self.buttons = Buttons(self)
        self.color = BASECOLOR
        self.local_server = None
        self.has_defier = False
        # sert juste pour visualiser, actualise_list sera appelé par le serveur à chaque fois
        self.actualise_list(self.dico_list)
        self.Window.mainloop()  
    
    def open_window(self):
        self.enregistrer_pseudo()
        self.enregistrer_port()
        self.enregistrer_host()
        self.enregistrer_adversaire()
        
        if self.nickname != NICKNAME :
            # va falloir mettre adversaire en argument
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

    def enregistrer_adversaire(self):
        self.adversaire=self.buttons.e_adversaire.get()
    
    def actualise_list(self,dico_list):
         #avant ça il faut supprimer l'ancienne liste affichée
         self.buttons.afficher_liste_joueur(self.trier_liste(dico_list))       

    def trier_liste(self,dico_list):
        """
            Prend le dico_list et le trie pour qu'il soit affichable dans buttons
        """
        Liste_score_joueur=[]
        for i in range(0,len(dico_list)):
            a=dico_list[i]["score"]
            Liste_score_joueur.append(a)
        Liste_score_joueur.sort()

        Liste_joueur=[]
        for i in Liste_score_joueur:
            for j in range(0,len(dico_list)):
                if i==dico_list[j]["score"] and dico_list[j]["name"] not in Liste_joueur:
                    a=dico_list[j]["name"]
                    Liste_joueur.append(a)
                    b=dico_list[j]["score"]
                    Liste_joueur.append(b)
        return Liste_joueur

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
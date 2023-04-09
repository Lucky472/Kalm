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
BACKGROUNDCOLOR = '#41B77F'
FONT = 'arial'
WIDTHWALL = 10
WIDTHLINE = 4
WIDTHFRAME = BOARD_X_LENGTH
HEIGHTFRAME = BOARD_Y_LENGTH//4
COLORLINE = "#D4D4D4"
COLORWALL = "#4d8b2b"
LENGTH_LINE = 10
PIXEL_BOARD_X_LENGTH = X_AXIS_LENGTH * SIZESQUARE
PIXEL_BOARD_Y_LENGTH = Y_AXIS_LENGTH * SIZESQUARE
X_OFFSET = 10
Y_OFFSET = 10
SPACING = 4
INITWALL = 7
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

ME = 0
OPPONENT = 1


class Client(ConnectionListener):
    def __init__(self, host, port, window,color,nickname):
        self.window = window
        self.color = color
        self.nickname = nickname
        self.opponent_color = "#f3f300"
        self.state=INITIAL
        self.Connect((host, port))
        print("Client started")
        print("Ctrl-C to exit")

    def Network_initplayer(self,data):
        """
        Envoie les nom et couleur de son joueur
        """
        connection.Send({"action": "init_player", "nickname": self.nickname, "color": self.color})

    def Network_connected(self, data):
        print("You are now connected to the server")
    
    def Network_connexion_accepted(self,data):
        self.window.show_tournament()
    
    def Network_connexion_denied(self,data):
        #dit au jouerur que la connexion a été refusée pour cause de mauvais pseudo
        sleep(2)
        self.window.destroy()
        self.state = DEAD
    
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
        self.window.destroy()
    
    def Network_placed_wall(self,data):
        self.window.controller.controller_place_wall(data["location"], data["orientation"])
        self.window.controller.opponent_walls.set(self.window.controller.opponent_walls.get()-1)
        self.window.controller.set_active()
        
    def Network_moved_pawn(self,data):
        self.window.controller.controller_move_pawn(self.window.controller.opponent_pawn, data["location"])
        self.window.controller.set_active()
        
    def Network_challenge(self,data):
        if self.window.ask_challenge(data["opponent_nickname"]):
            self.Send({"action":"challenge_accepted","challenged":self.nickname,"opponent_nickname":data["opponent_nickname"]})
        else :
            self.Send({"action":"challenge_denied","opponent":data["opponent_nickname"]})
    
    def Network_launch_game(self,data):
        self.window.launch_game(data["your_pawn"],data["opponent_pawn"],data["your_color"],data["opponent_color"],data["your_nickname"],data["opponent_nickname"])
    
    def Network_cannot_challenge(self,data):
        """
        indique au joueur que il ne peut pas défier le joueur
        (data["opponent"]) est le joueur ne pouvant pas être défié
        """
        boxedmessage.showinfo(title=None, message="Le joueur: "+data["opponent_nickname"]+" ne peut pas être défié")
    
    def Network_challenge_denied(self,data):
        self.window.challenge_denied(data["opponent_nickname"])
        
    def Network_close_game(self,data):
        self.window.show_tournament()
        
    def Network_update_leaderboard(self,data):
        self.window.update_leaderboard(data["leaderboard"])
    
    
#########################################################

class ClientWindow(Tk):
    def __init__(self, host, port,color,nickname):
        Tk.__init__(self)
        self.geometry("840x840")
        self.configure(bg=BACKGROUNDCOLOR)
        self.client = Client(host, int(port), self,color,nickname)
        self.controller = None
        self.f_affichage_liste=Frame(self,bg='white',bd=2,relief=SUNKEN)
        self.f_affichage_liste.pack(expand=YES, side=RIGHT)
        self.L_joueur = []
        self.Label_liste=Label(self.f_affichage_liste,text='Classement joueurs',font=(FONT,10),bg='white',fg ='black')
        self.Label_liste.pack()
        self.f_liste = Frame(self.f_affichage_liste,bg='white')
    
    def set_tournament(self):
        self.bind('<Return>',self.defy_tournament)
        self.text_tournament()
        self.pack_tournament()

    def unset_tournament(self):
        self.unbind('<Return>')
        self.frame.destroy()
        self.f_adversaire.destroy()
        self.B_jouer.destroy()

    def myMainLoop(self):
        while self.client.state!=DEAD:   
            self.update()
            self.client.Loop()
            sleep(0.001)
        exit()    

    
    def show_tournament(self):
        """
        unpack tt le jeu si il existe puis génère et pack tt l'interface de tournoi
        """
        if self.controller != None:
            self.unpack_game()
            self.set_tournament()
        else:
            self.set_tournament()


    def ask_challenge(self,opponent_nickname):
        """
        demande au joueur si il accepte le défi lancé par un joueur tiers
        (si oui, return True
         si non, return False)
        """ 
        answer = boxedmessage.askyesno(title = "Défi de "+ str(opponent_nickname),message =str(opponent_nickname)+" vous défie, voulez vous accepter ?")
        if answer == YES:
            return True
        return False

    def send_challenge(self,opponent_nickname):
        """
        fonction appellée par le bouton d'envoi de défi
        """
        self.client.Send({"action":"new_game_request","challenged":opponent_nickname})

    def challenge_denied(opponent):
        """
        opponent est un string
        informe le joueur que le défi a été refusé
        """
        boxedmessage.showinfo(title=None, message="TU AS ÉTÉ REJETÉ PAR" + opponent)

        
    def launch_game(self,my_pawn,opponent_pawn,my_color,opponent_color,my_nickname,opponent_nickname):
        self.unset_tournament()
        self.controller = Controller(self,self.client,my_pawn,opponent_pawn,my_color,opponent_color,my_nickname,opponent_nickname)

    def unpack_game(self):
        self.controller.view.unpack_all() 
        self.controller.view.f_labels.destroy()  
        self.controller = None

    def pack_tournament(self):
        self.frame.pack(pady=20)
        self.L_adversaire.pack()
        self.e_adversaire.pack()
        self.f_adversaire.pack()
        self.B_jouer.pack(side=BOTTOM)
    
    def text_tournament(self):
        self.frame=Frame(self,bg=BACKGROUNDCOLOR)
        self.f_adversaire=Frame(self.frame,bg=BACKGROUNDCOLOR)
        self.L_adversaire=Label(self.frame,text='Choisis ton adversaire',font=(FONT,19),bg=BACKGROUNDCOLOR,fg='white')
        self.e_adversaire=Entry(self.f_adversaire,font=(FONT,20),bg='white',fg='black')
        self.B_jouer = Button(self,text='   Défier   ',command=self.defy_tournament ,bg='#4065A4')

    def defy_tournament(self,evt):
        opponent = self.e_adversaire.get()
        if len(opponent) == 0:
            boxedmessage.showinfo(title=None, message="ON NE PEUT PAS DÉFIER LE VIDE GROS MALIN")
        else:
            list_nicknames = [p["nickname"] for p in self.leaderboard]
            if opponent in list_nicknames :
                self.send_challenge(opponent)
            else :
                boxedmessage.showinfo(title=None, message="CE GARS N'EXISTE PAS")

    """
    def trier_liste(self,dico_list):
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
    """

    def string_state(self,state):
        if state == 0:
            return "en attente"
        if state == 1:
            return "en partie"
        if state == 2:
            return "en attente de défi"

    def afficher_liste_joueur(self,liste_joueur):
        for player in liste_joueur:
            state = self.string_state(player["state"])
            self.L_joueur.append(Label(self.f_liste,text=player["nickname"]+" "+ str(player["score"])+" "+ state,font=(FONT,10),bg='#4065A4',fg='black',bd=2,relief=SUNKEN))
            self.L_joueur[-1].pack(pady=0,fill=X)

    def update_leaderboard(self,leaderboard):
        leaderboard = self.sorted_leaderboard(leaderboard)
        self.leaderboard = leaderboard
        for joueur in self.L_joueur :
            joueur.destroy()
        self.f_liste.destroy()
        self.f_liste = Frame(self.f_affichage_liste,bg='white')
        self.f_liste.pack(expand=YES,pady=30,padx=80)
        self.afficher_liste_joueur(leaderboard)
        
    def sorted_leaderboard(self,leaderboard):
        return sorted(leaderboard, key=lambda x: x["score"],reverse=True)


class Controller:
    def __init__(self,window,client,my_pawn,opponent_pawn,my_color,opponent_color,my_nickname,opponent_nickname):
        self.window = window
        self.client = client
        self.my_nickname = my_nickname
        self.opponent_nickname = opponent_nickname
        self.my_walls = IntVar()
        self.my_walls.set(INITWALL)
        self.opponent_walls = IntVar()
        self.opponent_walls.set(INITWALL)
        self.model = Model()
        #LE CONTROLLEUR DOIT FOURNIR LA COULEUR DU JOUEUR PUIS LA COULEUR DE L'ADVERSAIRE
        self.view = View(self,window,my_pawn,opponent_pawn,my_color,opponent_color)
        self.view.canvas_board.bind("<Button-1>",self.board_click)
        self.move = MOVE_PAWN
        self.state = INITIAL
        self.my_pawn = my_pawn
        self.opponent_pawn = opponent_pawn
        self.my_nickname = my_nickname
        self.opponent_nickname = opponent_nickname
        self.my_walls = IntVar()
        self.my_walls.set(INITWALL)
        self.opponent_walls = IntVar()
        self.opponent_walls.set(INITWALL)

        if self.my_pawn == "UP":
            self.set_active()
        else : 
            self.set_inactive()
    
    def set_active(self):
        self.state = ACTIVE
        if self.move == MOVE_PAWN:
            x,y = self.model.pawns[self.my_pawn].coords
            self.view.show_plays(self.model.accessible_from((x,y)))
        
    def set_inactive(self):
        self.state = INACTIVE
    
    def board_click(self,evt):
        if (self.state == ACTIVE):
            if (self.move == PLACE_WALL_UP) and (self.my_walls.get() > 0): 
                hole = self.detect_clicked_hole(evt.x,evt.y)
                if (hole != None):
                    if self.model.test_add_wall((hole[0],hole[1]),"UP"):
                        self.controller_place_wall((hole[0],hole[1]),"UP")
                        self.send_placed_wall((hole[0],hole[1]),"UP")
                        self.my_walls.set(self.my_walls.get()-1)
                    else:
                        boxedmessage.showinfo(title=None, message="TU PEUX PAS LE METTRE LA !")
            if (self.move == PLACE_WALL_ACROSS)and (self.my_walls.get() > 0): 
                print("clic side")
                hole = self.detect_clicked_hole(evt.x,evt.y)
                if (hole != None):
                    if self.model.test_add_wall((hole[0],hole[1]),"ACROSS"):
                        self.controller_place_wall((hole[0],hole[1]),"ACROSS")
                        self.send_placed_wall((hole[0],hole[1]),"ACROSS")
                        self.my_walls.set(self.my_walls.get()-1)
            if self.move == MOVE_PAWN :
                square = self.detect_clicked_square(evt.x,evt.y)
                if square != None and square in self.model.accessible_from(self.model.pawns[self.my_pawn].coords):
                    self.controller_move_pawn(self.my_pawn, square)
                    self.send_moved_pawn(square)


    def controller_move_pawn(self,pawn, location):
        self.view.delete_deletable_dots()
        x,y = location
        self.view.move_pawn(x, y, pawn)
        self.model.move_pawn(pawn, location)
        self.is_it_end_game()
        self.state = INACTIVE
        
    def is_it_end_game(self):
        if self.test_end_game() :
            if self.did_i_won() :
                self.send_i_won()
                self.view.show_winner(ME)
            else :
                self.send_i_lost()
                self.view.show_winner(OPPONENT)
    
    def did_i_won(self):
        if self.my_pawn == "DOWN" and self.model.pawns["DOWN"].coords[1] == 0:
            return True
        if self.my_pawn == "UP" and self.model.pawns["UP"].coords[1] == BOARD_Y_LENGTH-1:
            return True
        return False
    
    def send_i_lost(self):
        self.client.Send({"action":"i_lost"})
        
    def send_i_won(self):
        self.client.Send({"action":"i_won"})
    
    def test_end_game(self):
        return (self.model.pawns["DOWN"].coords[1] == 0) or (self.model.pawns["UP"].coords[1] == BOARD_Y_LENGTH -1)
    
    def controller_place_wall(self,location,orientation):
        x,y = location
        self.view.place_wall(x,y,orientation)  
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
                    if (pixel_y >= y_minus) and (pixel_y <= y_maxus):
                        return (2*x -1, 2*y -1)
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
                        return (2*x,2*y)
    
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
        self.view.show_plays(self.model.accessible_from((x,y)))
        
class View:
    def __init__(self,controller,window,my_pawn,opponent_pawn,color,opponent_color):
        self.controller = controller
        self.window = window
        self.canvas_board = Canvas(self.window,height = PIXEL_BOARD_Y_LENGTH + 2*Y_OFFSET,width =  PIXEL_BOARD_X_LENGTH + 2*X_OFFSET,bg =COLORBOARD )
        self.draw_board()
        # La grille commence à (0,0) donc les coordonnées données vont jusqu'à (6,6) pour une taille de 7 cases
        if my_pawn == "UP":
            self.pawns = {opponent_pawn:self.draw_pawn(BOARD_X_LENGTH // 2,BOARD_Y_LENGTH-1 , opponent_color),my_pawn:self.draw_pawn(BOARD_X_LENGTH // 2, 0,color)}
        else:
            self.pawns = {my_pawn:self.draw_pawn(BOARD_X_LENGTH // 2,BOARD_Y_LENGTH-1 ,color),opponent_pawn:self.draw_pawn(BOARD_X_LENGTH // 2, 0,opponent_color)}
        self.my_pawn = my_pawn
        self.opponent_pawn = opponent_pawn
        self.color = color 
        self.opponent_color = opponent_color
        self.deletable_dots = []        
        self.frame_buttons()
        self.frame_labels()
        self.buttons()
        self.pack_buttons()

        self.name_labels()
        self.walls_left_labels()


        self.pack_labels()
        self.canvas_board.pack(side=TOP)

    def name_labels(self):
        #FAUDRA CHANGER LA LISTE SELF.NAME
        self.L_name_left = Label(self.f_labels, text = self.controller.my_nickname)
        self.L_name_right = Label(self.f_labels, text = self.controller.opponent_nickname)
    
    def walls_left_labels(self):
        self.L_wall_left = Label(self.f_labels, textvariable = str(self.controller.my_walls))
        self.L_wall_middle = Label(self.f_labels, text = "WALLS LEFT" + " ")
        self.L_wall_right = Label(self.f_labels, textvariable = str(self.controller.opponent_walls))

    def frame_buttons(self):
        self.f_buttons = Frame(self.window, width = WIDTHFRAME, height = HEIGHTFRAME)

    def frame_labels(self):
        self.f_labels = Frame(self.window, width = WIDTHFRAME, height = HEIGHTFRAME)

    def buttons(self):
       self.B_move = Button(self.f_buttons, text = "Se déplacer", command = self.controller.set_move_pawn)
       self.B_horizontal_wall = Button(self.f_buttons, text = "Mur horizontal", command = self.controller.set_wall_horizontal)
       self.B_vertical_wall = Button(self.f_buttons, text = "Mur vertical", command = self.controller.set_wall_vertical)
    
    def pack_labels(self):
        self.f_labels.pack(side=TOP)
        self.L_name_left.pack(side=LEFT, padx=PIXEL_BOARD_X_LENGTH//4,expand=YES)
        self.L_name_right.pack(side=RIGHT, padx=PIXEL_BOARD_X_LENGTH//4, expand=YES)
        self.L_wall_left.pack(side=LEFT)
        self.L_wall_middle.pack(side = LEFT)
        self.L_wall_right.pack(side=RIGHT)
        
    def pack_buttons(self):
        self.f_buttons.pack(side=BOTTOM)
        self.B_horizontal_wall.pack(side=LEFT)
        self.B_move.pack(side=LEFT,padx = PIXEL_BOARD_X_LENGTH//3)
        self.B_vertical_wall.pack(side=RIGHT)

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

    def draw_pawn(self,x,y,color):
        x0,y0 = self.get_center(x,y)
        idd =  self.canvas_board.create_oval(x0 - RADIUSPAWN,y0-RADIUSPAWN,x0 + RADIUSPAWN,y0 + RADIUSPAWN,fill = color)
        return idd
    
    def get_center(self,x,y):
        x0 = (x//2)*SIZESQUARE + X_OFFSET + SIZESQUARE//2
        y0 = (y//2)*SIZESQUARE + Y_OFFSET + SIZESQUARE//2
        return (x0,y0)

    def delete_pawn(self,pawn_id):
        self.canvas_board.delete(self.pawns.pop(pawn_id))
        
    def move_pawn(self,x,y,pawn_id):
        self.delete_pawn(pawn_id)
        if pawn_id == self.my_pawn:
            color = self.color
        else:
            color = self.opponent_color
        self.pawns[pawn_id] = self.draw_pawn(x,y,color)
    
    def place_wall(self,x,y,orientation):
        new_x = x // 2 +1
        new_y = y // 2 +1
        if orientation == "ACROSS":
            self.place_horizontal_wall(new_x,new_y)
        elif orientation == "UP":
            self.place_vertical_wall(new_x,new_y)

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
        y0 = (y-1)*SIZESQUARE +Y_OFFSET +SPACING
        x1 = x*SIZESQUARE +X_OFFSET - WIDTHLINE
        y1 = (y+1)*SIZESQUARE +Y_OFFSET -SPACING
        self.canvas_board.create_rectangle(x0,y0,x1,y1,fill = COLORWALL)

    def place_horizontal_wall(self,x,y):
        y0 = y*SIZESQUARE +Y_OFFSET + WIDTHLINE
        x0 = (x-1)*SIZESQUARE +X_OFFSET +SPACING
        y1 = y*SIZESQUARE +Y_OFFSET - WIDTHLINE
        x1 = (x+1)*SIZESQUARE +X_OFFSET -SPACING
        self.canvas_board.create_rectangle(x0,y0,x1,y1,fill = COLORWALL)
        
    def show_winner(self,winner):
        if winner == ME:
            """
            indique que j'ai gagné
            """
            boxedmessage.showinfo(title=None, message="BIEN JOUÉ TU ES LE MEILLEUR JOUEUR")
        else:
            """
            indique que j'ai perdu
            """
            boxedmessage.showinfo(title=None, message="TU AS PERDU ... ")
            
    def unpack_all(self):
        self.canvas_board.destroy()
        self.f_buttons.destroy()
        self.B_horizontal_wall.destroy()
        self.B_move.destroy()
        self.B_vertical_wall.destroy()

class Model :
    def __init__(self):
        self.board = self.new_board()
        self.pawns = {"UP":Pawn((BOARD_X_LENGTH // 2, 0)), "DOWN":Pawn((BOARD_X_LENGTH // 2, BOARD_Y_LENGTH -1))}
    
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
                print("faux car occupé")
                return False
        if orientation == "ACROSS":
            if self.board[x-1][y].occupied or self.board[x][y].occupied or self.board[x+1][y].occupied :
                print("faux car occupé")
                return False
        print("on fait le pathfind")
        return self.pathfind_test_with_wall(location,orientation)
    
    def accessible_from(self,location,avoid = None):
        x,y = location
        accessible_squares = []
        #aller à gauche
        if x != 0 :
            if not self.board[x-1][y].occupied:
                if not self.board[x-2][y].occupied:
                    accessible_squares.append((x-2,y))
                elif (x-2,y) != avoid:
                    for square in self.accessible_from((x-2,y),avoid = location):
                        accessible_squares.append(square)
        #aller à droite
        if x != BOARD_X_LENGTH -1 :
            if not self.board[x+1][y].occupied:
                if not self.board[x+2][y].occupied:
                    accessible_squares.append((x+2,y))
                elif (x+2,y) != avoid:
                    for square in self.accessible_from((x+2,y),avoid = location):
                        accessible_squares.append(square)
        #aller en haut
        if y != 0 :
            if not self.board[x][y-1].occupied:
                if not self.board[x][y-2].occupied:
                    accessible_squares.append((x,y-2))
                elif (x,y-2) != avoid:
                    for square in self.accessible_from((x,y-2),avoid = location):
                        accessible_squares.append(square)
        #aller en bas
        if y != BOARD_Y_LENGTH -1:
            if not self.board[x][y+1].occupied:
                if not self.board[x][y+2].occupied:
                    accessible_squares.append((x,y+2))
                elif (x,y+2) != avoid:
                    for square in self.accessible_from((x,y+2),avoid = location):
                        accessible_squares.append(square)
        return accessible_squares
    
    def pathfind_test_with_wall(self,location,orientation):
        self.add_wall(location, orientation)
        test = True
        for key in self.pawns:
            pawn = self.pawns[key]
            if key == "DOWN":
                test = test and (self.pathfind_test(pawn.coords, 0))
            else :
                test = test and (self.pathfind_test(pawn.coords, BOARD_Y_LENGTH-1))
        self.remove_wall(location, orientation)
        print(test)
        return test
    
    def pathfind_test(self,location,targeted_y,all_accessibles=[],new_accessibles=[]):
        if all_accessibles == []:
            acc = list(self.accessible_from(location))
            new_accessibles = acc
            all_accessibles = acc
            all_accessibles.append(location)
        else: 
            border = []
            for new_square in new_accessibles:
                for square in self.accessible_from(new_square):
                    if square not in all_accessibles:
                        if square[1] == targeted_y:
                            return True
                        border.append(square)
                        all_accessibles.append(square)
            new_accessibles = border
        if len(new_accessibles) == 0:
            return False
        return self.pathfind_test(location,targeted_y,all_accessibles=all_accessibles,new_accessibles=new_accessibles)

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
        self.frame=Frame(self.menu.Window,bg=BACKGROUNDCOLOR)
        self.f_pseudo= Frame(self.frame,bg=BACKGROUNDCOLOR)
        self.f_host = Frame(self.frame,bg=BACKGROUNDCOLOR)
        self.f_port = Frame(self.frame,bg=BACKGROUNDCOLOR)
        
        
    def text(self):
        self.Labeltitle1=Label(self.frame,text='Menu du jeu quoridor',font=(FONT,30),bg=BACKGROUNDCOLOR,fg='white')
        self.Labeltitle2=Label(self.frame,text='Préparez vous à jouer, regarder les règles et choississez votre couleur',font=(FONT,10),bg='#41B77F',fg='white')
        self.L_pseudo=Label(self.frame,text='Choisis ton pseudo',font=(FONT,19),bg=BACKGROUNDCOLOR,fg='white')
        self.L_host=Label(self.frame,text='Host',font=(FONT,19),bg=BACKGROUNDCOLOR,fg='white')
        self.L_port = Label(self.frame,text='Port',font=(FONT,19),bg=BACKGROUNDCOLOR,fg='white')

    def buttons(self):
        self.B_quitter=Button(self.menu.Window,text='Quitter',command=self.menu.Window.destroy,bg='#ed1111')
        self.B_couleur=Button(self.frame,text='Selectionner une couleur',command=self.menu.change_color,bg='#4065A4')
        self.B_jouer = Button(self.menu.Window,text='   Jouer   ',command= self.menu.open_window,bg='#4065A4')

    def entries(self):
        self.e_pseudo=Entry(self.f_pseudo,font=(FONT,20),bg='white',fg='black')
        self.e_host = Entry(self.f_host,font=(FONT,20),bg='white',fg='black')
        self.e_port = Entry(self.f_port,font=(FONT,20),bg='white',fg='black')
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
        self.Window.config(background=BACKGROUNDCOLOR)
        self.buttons = Buttons(self)
        self.color = BASECOLOR
        self.local_server = None
        self.has_defier = False
        # sert juste pour visualiser, actualise_list sera appelé par le serveur à chaque fois
        self.Window.mainloop()  
    
    def open_window(self):
        self.enregistrer_pseudo()
        self.enregistrer_port()
        self.enregistrer_host()

        if len(self.nickname) >= 22:
            boxedmessage.showinfo(title=None, message="TON PSEUDO EST TROP LONG!")

        if (self.nickname != NICKNAME) or (len(self.nickname)==0):
            self.client_window = ClientWindow(self.host, self.port, self.color, self.nickname)
            self.client_window.myMainLoop()
            
        else :
            boxedmessage.showinfo(title=None, message="CHANGE TON PSEUDO ! ET NE MET PAS LE VIDE !") 

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

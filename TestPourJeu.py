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
WIDTHWALL = 20
WIDTHLINE = 4
COLORLINE = "#D4D4D4"
COLORWALL = "#AA5372"
LENGTH_LINE = 10
PIXEL_BOARD_X_LENGTH = X_AXIS_LENGTH * SIZESQUARE
PIXEL_BOARD_Y_LENGTH = Y_AXIS_LENGTH * SIZESQUARE
WIDTHFRAME = BOARD_X_LENGTH
HEIGHTFRAME = BOARD_Y_LENGTH//4
X_OFFSET = 10
Y_OFFSET = 10
SPACING = 4


HOST, PORT = "localhost", "31425"
NICKNAME = "nick"
BASECOLOR = "#ca7511"

INITIAL=0
ACTIVE=1
DEAD=-1

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
    
#########################################################

class ClientWindow(Tk):
    #c'est lui notre controller
    def __init__(self, host, port,color,nickname):
        Tk.__init__(self)
        self.client = Client(host, int(port), self,color,nickname)
        self.controller = Controller(self)
        

    def myMainLoop(self):
        while self.client.state!=DEAD:   
            self.update()
            self.client.Loop()
            sleep(0.001)
        exit()    

class Controller:
    def __init__(self,window):
        self.model = Model()
        self.view = View(window,"#000000","#726A62")
        self.view.canvas_board.bind("<Button-1>",self.board_click)
        self.move = MOVE_PAWN
        self.state = INITIAL
    
    def frame_buttons(self,window):
        self.f_buttons = Frame(self.window, width = WIDTHFRAME, height = HEIGHTFRAME).pack(side=BOTTOM)
    
    def buttons(self):
       self.B_move = Button(self.f_buttons, text = "Se déplacer", command = self.controller.set_move_pawn()).pack(side=LEFT)
       self.B_horizontal_wall = Button(self.f_buttons, text = "Mur horizontal", command = self.controller.set_wall_horisontal()).pack(side=LEFT, padx=PIXEL_BOARD_X_LENGTH//3)
       self.B_vertical_wall = Button(self.f_buttons, text = "Mur vertical", command = self.controller.set_wall_vertical()).pack(side=LEFT)
    
    def board_click(self):
        if self.state == ACTIVE :
            pass
    
    def set_wall_vertical(self):
        self.move = PLACE_WALL_UP
                
    def set_wall_horisontal(self):
        self.move = PLACE_WALL_ACROSS
    
    def set_move_pawn(self):
        self.move = MOVE_PAWN
        

class View:
    def __init__(self,window,color,oponent_color):
        self.window = window
        self.canvas_board = Canvas(self.window,height = PIXEL_BOARD_Y_LENGTH + 2*Y_OFFSET,width =  PIXEL_BOARD_X_LENGTH + 2*X_OFFSET,bg =COLORBOARD )
        self.canvas_board.bind("<Button-1>",self.detect_clicked_square)
        self.draw_board()

        self.canvas_board.pack()
        # La grille commence à (0,0) donc les coordonnées données vont jusqu'à (6,6)
        self.pawns = {"DOWN":self.draw_pawn(X_AXIS_LENGTH // 2,Y_AXIS_LENGTH-1 ,"#67E3A8"),"UP":self.draw_pawn(X_AXIS_LENGTH // 2, 0,"#000000")}
        print(self.pawns)

        self.canvas_board.pack()
        self.color = color 
        self.oponent_color = oponent_color
        # La grille commence à (0,0) donc les coordonnées données vont jusqu'à (6,6)
        self.pawns = {"DOWN":self.draw_pawn(X_AXIS_LENGTH // 2,Y_AXIS_LENGTH-1,self.color),"UP":self.draw_pawn(X_AXIS_LENGTH // 2, 0,self.oponent_color)}
        #Pour gérer la couleur faudra savoir la couleur du bas et celle du haut
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

#PAS CENSE ÊTRE LA, mais pour tester la fonction
    def detect_clicked_square(self,evt):
        print("clic")
        pixel_x = evt.x
        pixel_y = evt.y
        for x in range(0,X_AXIS_LENGTH):
            x_minus = x*SIZESQUARE + X_OFFSET + WIDTHLINE
            x_maxus = (x+1)*SIZESQUARE + X_OFFSET - WIDTHLINE
            for y in range(0,Y_AXIS_LENGTH):
                y_minus = y*SIZESQUARE + Y_OFFSET + WIDTHLINE
                y_maxus = (y+1)*SIZESQUARE + Y_OFFSET - WIDTHLINE
                #self.canvas_board.create_rectangle(x_minus,y_minus,x_maxus,y_maxus,fill = "#000000")
                if (pixel_x >= x_minus) and (pixel_x <= x_maxus):
                    if (pixel_y >= y_minus) and (pixel_y <= y_maxus):
                        self.canvas_board.create_rectangle(x_minus,y_minus,x_maxus,y_maxus,fill = "#000000")
                        print(x,y)
                        return (x,y)
        
    def draw_pawn(self,x,y,color):
        x0,y0 = self.get_center(x,y)
        idd =  self.canvas_board.create_oval(x0 - RADIUSPAWN,y0-RADIUSPAWN,x0 + RADIUSPAWN,y0 + RADIUSPAWN,fill = color)
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
        if type == "horizontal":
            self.place_horizontal_wall(x,y)
        elif type == "vertical":
            self.place_vertical_wall(x,y)
    
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


"""client_window = ClientWindow(host, port)
client_window.myMainLoop()

tests
view.place_horizontal_wall(3,2)
view.place_horizontal_wall(1,2)
view.place_vertical_wall(5,1)


for x in range(1,X_AXIS_LENGTH):
     x_minus = x*SIZESQUARE + X_OFFSET - LENGTH_LINE
     x_maxus = (x)*SIZESQUARE + X_OFFSET + LENGTH_LINE
     for y in range(0,Y_AXIS_LENGTH):
            y0 = y*SIZESQUARE + Y_OFFSET - LENGTH_LINE
            y1 = (y)*SIZESQUARE + Y_OFFSET + LENGTH_LINE
            view.show_plays([(x,y)])
            if x%2 == 0:
                view.canvas_board.create_rectangle(x_minus,y0,x_maxus,y1,fill = "#000000")
            else :
                view.canvas_board.create_rectangle(x_minus,y0,x_maxus,y1,fill = "#682925")
"""

window = Tk()
#controller = Controller(window)
view = View(window,"#AA5325","#E52627")
window.mainloop()

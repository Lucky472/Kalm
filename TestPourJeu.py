from tkinter import *
Y_AXIS_LENGTH = 7
X_AXIS_LENGTH = 7
BOARD_X_LENGTH = 2 * X_AXIS_LENGTH - 1
BOARD_Y_LENGTH = 2 * Y_AXIS_LENGTH - 1
SIZESQUARE = 50
RADIUSPAWN = 17
COLORBOARD = "#454545"
WIDTHWALL = 10
WIDTHLINE = 4
COLORLINE = "#D4D4D4"
LENGTH_LINE = 10
PIXEL_BOARD_X_LENGTH = X_AXIS_LENGTH * SIZESQUARE
PIXEL_BOARD_Y_LENGTH = Y_AXIS_LENGTH * SIZESQUARE
X_OFFSET = 10
Y_OFFSET = 10
class View:
    def __init__(self,window):
        self.window = window
        self.canvas_board = Canvas(self.window,height = PIXEL_BOARD_Y_LENGTH + 2*Y_OFFSET,width =  PIXEL_BOARD_X_LENGTH + 2*X_OFFSET,bg =COLORBOARD )
        self.draw_board()
        self.canvas_board.pack()
        # La grille commence à (0,0) donc les coordonnées données vont jusqu'à (6,6)
        self.pawns = {"DOWN":self.draw_pawn(X_AXIS_LENGTH // 2,Y_AXIS_LENGTH-1 ),"UP":self.draw_pawn(X_AXIS_LENGTH // 2, 0)}
        print(self.pawns)
        
    def draw_board(self):
        #Lignes verticales
        for x in range(X_AXIS_LENGTH+1):
            x01 = SIZESQUARE*x + X_OFFSET
            for y in range (Y_AXIS_LENGTH):
                y0 = y*SIZESQUARE + LENGTH_LINE + Y_OFFSET
                y1 = (y+1)*SIZESQUARE - LENGTH_LINE + Y_OFFSET
                self.canvas_board.create_line(x01,y0,x01,y1,fill = COLORLINE,width=WIDTHLINE)
        #Lignes horizontales
        for y in range(Y_AXIS_LENGTH+1):
            y01 = SIZESQUARE*y + Y_OFFSET
            for x in range (X_AXIS_LENGTH):
                x0 = x*SIZESQUARE + LENGTH_LINE + X_OFFSET
                x1 = (x+1)*SIZESQUARE - LENGTH_LINE + X_OFFSET 
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


window = Tk()
view = View(window)
window.mainloop()


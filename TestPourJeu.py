from tkinter import *
Y_AXIS_LENGTH = 7
X_AXIS_LENGTH = 7
BOARD_X_LENGTH = 2 * X_AXIS_LENGTH - 1
BOARD_Y_LENGTH = 2 * Y_AXIS_LENGTH - 1
SIZESQUARE = 20
COLORSQUARE = "#A567A3"
WIDTHWALL = 10

class View:
    def __init__(self,window,board):
        self.window = window
        self.board = board
        self.canvas_board = Canvas(self.window)
        self.draw_board(board)
        self.canvas_board.pack()
    
    def draw_board(self,board):
        for x in range(BOARD_X_LENGTH):
            for y in range (BOARD_Y_LENGTH):
                self.board[x][y] = self.canvas_board.create_rectangle(x*SIZESQUARE,y*SIZESQUARE,(x+1)*SIZESQUARE,(y+1)*SIZESQUARE,fill = COLORSQUARE)

                if self.is_square(x,y):
                    self.board[x][y] = self.canvas_board.create_rectangle(x*SIZESQUARE,y*SIZESQUARE,(x+1)*SIZESQUARE,(y+1)*SIZESQUARE,fill = COLORSQUARE)
                else:
                    self.board[x][y] = self.canvas_board.create_rectangle(x*SIZESQUARE,y*SIZESQUARE,(x+1)*SIZESQUARE,(y+1)*SIZESQUARE,fill = "#0A8637")
    def is_square(self,x,y):
        return (x % 2 == 0) and (y % 2 == 0)

class Square:
    def __init__(self):
        pass
class Hole:
    def __init__(self):
        pass

board = [[0 for j in range(BOARD_Y_LENGTH)] for i in range(BOARD_X_LENGTH)]
def return_board(board):
    for x in range(BOARD_X_LENGTH):
        for y in range (BOARD_Y_LENGTH):
            if (x%2 == 0) and (y%2 ==0):
                board[x][y] = Square()
            else :
                board[x][y] = Hole()
    return board



window = Tk()
view = View(window,return_board(board))
window.mainloop()


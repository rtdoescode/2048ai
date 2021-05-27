# This file is part of the open source 2048 game itself
# along with logic.py.
# It's not part of my implementation of the NEAT algorithm.
# Available here https://github.com/yangshun/2048-python


from tkinter import *
from logic import *
from random import *
import logic
import time
import genome
import threading
import networkthread

SIZE = 500
GRID_LEN = 4
GRID_PADDING = 10

BACKGROUND_COLOR_GAME = "#92877d"
BACKGROUND_COLOR_CELL_EMPTY = "#9e948a"
BACKGROUND_COLOR_DICT = {   2:"#eee4da", 4:"#ede0c8", 8:"#f2b179", 16:"#f59563", \
                            32:"#f67c5f", 64:"#f65e3b", 128:"#edcf72", 256:"#edcc61", \
                            512:"#edc850", 1024:"#edc53f", 2048:"#edc22e" }
CELL_COLOR_DICT = { 2:"#776e65", 4:"#776e65", 8:"#f9f6f2", 16:"#f9f6f2", \
                    32:"#f9f6f2", 64:"#f9f6f2", 128:"#f9f6f2", 256:"#f9f6f2", \
                    512:"#f9f6f2", 1024:"#f9f6f2", 2048:"#f9f6f2" }
FONT = ("Verdana", 40, "bold")

KEY_UP_ALT = "\'\\uf700\'"
KEY_DOWN_ALT = "\'\\uf701\'"
KEY_LEFT_ALT = "\'\\uf702\'"
KEY_RIGHT_ALT = "\'\\uf703\'"

KEY_UP = "'w'"
KEY_DOWN = "'s'"
KEY_LEFT = "'a'"
KEY_RIGHT = "'d'"

class GameGrid(Frame):
    def __init__(self,genome):
        Frame.__init__(self)

        self.queued_action = None
        self.ready = False
        self.thread_done = False
        
        self.grid()
        self.master.title('2048')
        self.master.bind("<Key>", self.key_down)
        self.network = None

        #self.gamelogic = gamelogic
        self.commands = {   KEY_UP: up, KEY_DOWN: down, KEY_LEFT: left, KEY_RIGHT: right,
                            KEY_UP_ALT: up, KEY_DOWN_ALT: down, KEY_LEFT_ALT: left, KEY_RIGHT_ALT: right }

        if genome != 0:
            self.network = networkthread.network_thread(genome,self)
        
        self.gameover = False
        self.final_score = 0
        
        self.grid_cells = []
        self.init_grid()
        self.init_matrix()
        self.update_grid_cells()

        self.ready = True
        logic.Score = 0

        while True:

            if self.queued_action != None:
                #print("mainloop processing key",self.queued_action)
                self.process_key(self.queued_action)
                self.queued_action = None
                self.ready = True

            if self.thread_done == True:
                self.network.join()
                self.quit()
                self.destroy()
                return
            
            self.update_idletasks()
            self.update()
            
    def close(self):
        self.quit()
        self.destroy()

    def game_is_over(self):
        return self.gameover

    def init_grid(self):
        background = Frame(self, bg=BACKGROUND_COLOR_GAME, width=SIZE, height=SIZE)
        background.grid()
        for i in range(GRID_LEN):
            grid_row = []
            for j in range(GRID_LEN):
                cell = Frame(background, bg=BACKGROUND_COLOR_CELL_EMPTY, width=SIZE/GRID_LEN, height=SIZE/GRID_LEN)
                cell.grid(row=i, column=j, padx=GRID_PADDING, pady=GRID_PADDING)
                # font = Font(size=FONT_SIZE, family=FONT_FAMILY, weight=FONT_WEIGHT)
                t = Label(master=cell, text="", bg=BACKGROUND_COLOR_CELL_EMPTY, justify=CENTER, font=FONT, width=4, height=2)
                t.grid()
                grid_row.append(t)

            self.grid_cells.append(grid_row)

    def gen(self):
        return randint(0, GRID_LEN - 1)

    def init_matrix(self):
        self.matrix = new_game(4)

        self.matrix=add_two(self.matrix)
        self.matrix=add_two(self.matrix)
	
    def calculate_score(self):
        fitness = logic.Score
        logic.Score = 0
        return fitness

    def update_grid_cells(self):
        for i in range(GRID_LEN):
            for j in range(GRID_LEN):
                new_number = self.matrix[i][j]
                if new_number == 0:
                    self.grid_cells[i][j].configure(text="", bg=BACKGROUND_COLOR_CELL_EMPTY)
                else:
                    self.grid_cells[i][j].configure(text=str(new_number), bg=BACKGROUND_COLOR_DICT[new_number], fg=CELL_COLOR_DICT[new_number])
        self.update_idletasks()
        
    def key_down(self, event):
        key = repr(event.char)
        self.process_key(key)

    def process_key(self, key):
        if key in self.commands:
            self.matrix,done = self.commands[key](self.matrix)
            if done:
                self.matrix = add_two(self.matrix)
                self.update_grid_cells()
                done=False
                if game_state(self.matrix)=='win':
                    self.gameover = True
                    self.grid_cells[1][1].configure(text="You",bg=BACKGROUND_COLOR_CELL_EMPTY)
                    self.grid_cells[1][2].configure(text="Win!",bg=BACKGROUND_COLOR_CELL_EMPTY)
                    self.grid_cells[2][1].configure(text=logic.Score,bg=BACKGROUND_COLOR_CELL_EMPTY)
                if game_state(self.matrix)=='lose':
                    self.gameover = True
                    self.grid_cells[1][1].configure(text="You",bg=BACKGROUND_COLOR_CELL_EMPTY)
                    self.grid_cells[1][2].configure(text="Lose!",bg=BACKGROUND_COLOR_CELL_EMPTY)
                    self.grid_cells[2][1].configure(text=logic.Score,bg=BACKGROUND_COLOR_CELL_EMPTY)
                    
    def generate_next(self):
        index = (self.gen(), self.gen())
        while self.matrix[index[0]][index[1]] != 0:
            index = (self.gen(), self.gen())
        self.matrix[index[0]][index[1]] = 2

    def get_inputs(self):

        inputs = []
        
        for i in range(GRID_LEN):
            for j in range(GRID_LEN):
                inputs.append(self.matrix[i][j])

        return inputs

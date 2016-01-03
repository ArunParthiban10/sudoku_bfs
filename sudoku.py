#!/usr/local/bin/python3

import copy
from queue import Queue
import sys
from tkinter import *
class Problem(object):

    def __init__(self, initial, goal=None):
        self.initial = initial
        self.goal = goal

    def actions(self, state):
        '''
        Return a list of possible actions
        '''
        return [x for x in range(1,len(state)+1)]

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        new_state=copy.deepcopy(state)
        for r in range(len(new_state)):
            for c in range(len(new_state[0])):
                if new_state[r][c] == 0:
                    new_state[r][c]= action
                    return new_state

    def goal_test(self, state):
        '''
        Check is the current state is the goal state. Goal state is when the 
        board is completely filled and there are no conflicts
        '''

        if not self.is_filled(state):
            return False

        if self.check_rcs(state):
            return False

        if self.check_boxes(state):
            return False
        return True

    def prune(self,state):
        '''
        This function will return True is the current state of the board 
        can never be part of a solution. Faslse otherwise.
        '''
        return (self.check_boxes(state) or self.check_rcs(state))

    def is_filled(self,state):
        '''
        This function returns true is the board has no blank cells. False otherwise.
        '''
        for row in state:
            if 0 in row:
                return False
        return True

    def check_rcs(self,state):
        ''' 
        This funciton checks all rows and columns to see if there are any conflicts.
        If there is a conflict, the function will return True. False otherwise.
        '''

        # Checks for rows
        for r in range(len(state)):
            histroy_list = [False]*10
            for c in range(len(state[0])):
                if histroy_list[state[r][c]]:
                    return True
                else:
                    if state[r][c]!=0:
                        histroy_list[state[r][c]] = True


        # Checks for cols
        for c in range(len(state[0])):
            histroy_list = [False]*10
            for r in range(len(state)):
                if histroy_list[state[r][c]]:
                    return True
                else:
                    if state[r][c]!=0:
                        histroy_list[state[r][c]] = True

        return False

    def check_boxes(self,state):

        '''
        This function checks sub boxes in the board for any conflicts. Returns True 
        if there is a conflict and false otherwise.
        '''
        board_len = len(state)
        box_len   = len(state)//3

        for colstart in range(0,board_len,3):
            for box in range(0,board_len-1,box_len):
                histroy_list = [False]*10
                for r in range (box,box+box_len):
                    for c in range(colstart,colstart+3):
                        if histroy_list[state[r][c]]:
                            return True
                        else:
                            if state[r][c]!=0:
                                histroy_list[state[r][c]] = True

        return False

class Node:

    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent=parent
        self.action=action
        self.depth = 0
        if parent:
            self.depth = parent.depth + 1

    def expand(self, problem):
        '''
        List of all nodes in the next level
        '''
        return [self.child_node(problem, action)
                for action in problem.actions(self.state)]

    def child_node(self, problem, action):
        next = problem.result(self.state, action)
        return Node(next, self, action)


def breadth_first_search(problem):
    node = Node(problem.initial)
    if problem.goal_test(node.state):
        return node

    frontier=Queue()
    frontier.put(node)

    while frontier.qsize()!=0:
        node = frontier.get()
        problem.initial=node.state

        for child in node.expand(problem):
            if problem.goal_test(child.state):
                return child

            # Pruneing
            if child != None and problem.prune(child.state) is False:
                frontier.put(child)

    return None

class  GUI:
    def __init__(self, n):
        self.board_size = n
        self.master = Tk()
        self.create_board()

    def create_board(self):
        '''
        Funtion creates all text cells and buttons required
        '''
        self. cells = [[None for r in range(self.board_size)] for c in range(self.board_size)]
        for row in range(self.board_size):
            for col in range(self.board_size):
                self.cells[row][col] = Entry(self.master, width=3)
                self.cells[row][col].grid(row=row,column=col)

        self.solve_button = Button(self.master, text="Solve", width=10, command=self.solve)
        self.clear_button = Button(self.master, text="Clear", width=10, command=self.clear)
        self.slider = Scale(self.master, from_=6, to=15,orient=HORIZONTAL)
        self.resize_button = Button(self.master, text="Resize", width=10, command=lambda : self.resize (self.slider.get()))

        self.solve_button.grid(row=0,column=self.board_size+1)
        self.clear_button.grid(row=1,column=self.board_size+1)
        self.slider.grid(row=2, column=self.board_size+1)
        self.resize_button.grid(row=3,column=self.board_size+1)

        self.controls = [self.solve_button,self.clear_button,self.resize_button,self.slider]

    def get_values(self):
        '''
        Returns values from the board as a 2 dimensional array. 0 represents empty cells
        '''
        values = [[0 for r in range(self.board_size)] for c in range(self.board_size)]
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.cells[row][col].get():
                    values[row][col] = int(self.cells[row][col].get())
        return values

    def set_values(self, new_vals):
        '''
        Given a set of new values, function will write them on the GUI board. 
        Old values will be replaced.

        :param new_vals: (two-dimensional list) containing new values
        '''
        values = [[0 for r in range(self.board_size)] for c in range(self.board_size)]
        for row in range(self.board_size):
            for col in range(self.board_size):
                self.cells[row][col].delete(0, END)
                self.cells[row][col].insert(0,new_vals[row][col])

    def clear(self):
        '''
        Clear values from all cells
        '''
        values = [[0 for r in range(self.board_size)] for c in range(self.board_size)]
        for row in range(self.board_size):
            for col in range(self.board_size):
                self.cells[row][col].delete(0, END)

    def resize(self,val):
        '''
        Resize board to the value passed in.

        :param val: (int) size of board 
        '''
        self.destroy_all()
        self.board_size=val
        self.create_board()

    def destroy_all(self):
        '''
        Destroy all buttons,cells, and slider from the board
        '''
        for row in range(self.board_size):
            for col in range(self.board_size):
                self.cells[row][col].destroy()

        for control in self.controls:
            control.destroy()


    def solve(self):
        '''
        Driver function
        '''
        values = self.get_values()
        p = Problem(values)
        solution = breadth_first_search(p)
        self.set_values(solution.state)

        
def main():
    board = GUI(6)
    mainloop()

if __name__ == "__main__":
    main()





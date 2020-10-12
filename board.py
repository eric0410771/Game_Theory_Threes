#!/usr/bin/env python3

"""
Basic framework for developing 2048 programs in Python

Author: Hung Guei (moporgic)
        Computer Games and Intelligence (CGI) Lab, NCTU, Taiwan
        http://www.aigames.nctu.edu.tw
"""
import numpy as np

class Constant:
    """ A constant class to map index to value of tile and score """
    def __init__(self):
        
        self._index_to_tile = np.array([0] * 15)
        self._index_to_score = np.array([0] * 15)
        self._build_table()
        
    def _build_table(self):
        
        self._index_to_tile[:4] = np.arange(4)
        
        for i in range(11):
            self._index_to_tile[i+4] = self._index_to_tile[i+3] * 2
        
        self._index_to_score[3] = 3
        for i in range(11):
            self._index_to_score[i+4] = self._index_to_score[i+3] * 3
            
    def index2tile(self, index):
        return self._index_to_tile[index]
    
    def index2score(self, index):
        return self._index_to_score[index]
        
class board:
    """ simple implementation of 2048 puzzle """
    feature_index = [[0,1,2,3,4,5],[3,7,11,15,2,6],[15,14,13,12,11,10],[3,2,1,0,7,6],[0,4,8,12,1,5],[12,13,14,15,8,9,],[15,11,7,3,14,10],[4,5,6,7,8,9],[2,6,10,14,1,5],[11,10,9,8,7,6],[13,9,5,1,14,10],[7,6,5,4,11,10],[1,5,9,13,2,6],[8,9,10,11,4,5],[14,10,6,2,13,9],[0,1,2,4,5,6],[3,7,11,2,6,10],[15,14,13,11,10,9],[12,8,4,13,9,5],[3,2,1,7,6,5],[0,4,8,1,5,9],[12,13,14,8,9,10],[15,11,7,14,10,6],[4,5,6,8,9,10],[2,6,10,1,5,9],[11,10,9,7,6,5],[13,9,5,14,10,6],[7,6,5,11,10,9],[1,5,9,2,6,10],[8,9,10,4,5,6],[14,10,6,13,9,5]]
    
    def __init__(self, state = None):
        self.state = state[:] if state is not None else [0] * 16
        self.constant_table = Constant()
        return
    def features(self):
        weight_index = []
        for feature_index in board.feature_index:
            index = 0
            for i in feature_index:
                index *= 11
                index += min(self.state[i], 10)
            weight_index.append(index)
        return weight_index
                
    def __getitem__(self, pos):
        return self.state[pos]
    
    def __setitem__(self, pos, tile):
        self.state[pos] = tile
        return
    
    def place(self, pos, tile):
        """
        place a tile (index value) to the specific position (1-d form index)
        return 0 if the action is valid, or -1 if not
        """
        if pos >= 16 or pos < 0:
            return -1
        if tile != 1 and tile != 2 and tile != 3:
            return -1
        self.state[pos] = tile
        return 0
    
    def slide(self, opcode):
        """
        apply an action to the board
        return the reward of the action, or -1 if the action is illegal
        """
        if opcode == 0:
            return self.slide_up()
        if opcode == 1:
            return self.slide_right()
        if opcode == 2:
            return self.slide_down()
        if opcode == 3:
            return self.slide_left()
        return -1
    
    def slide_left(self):
        move, score = [], 0
        for row in [self.state[r:r + 4] for r in range(0, 16, 4)]:
            buf = row + [0]
            merge = False
            while buf[0] and not merge: 
                if buf[0] == buf[1] and buf[0] >2:
                    buf = buf[1:]
                    buf[0] += 1
                    merge = True
                    score += self.constant_table.index2score(buf[0])
                    #score += 1
                elif buf[0] > 0 and buf[1] > 0 and buf[0] + buf[1] == 3:
                    buf = buf[1:]
                    buf[0] = 3
                    score += self.constant_table.index2score(buf[0])
                    #score += 1
                    merge = True
                move += [buf[0]]
                if not merge:
                    buf = buf[1:]
            move += buf[1:]
                
        if move != self.state:
            self.state = move
            return score
        return -1
    
    def slide_right(self):
        self.reflect_horizontal()
        score = self.slide_left()
        self.reflect_horizontal()
        return score
    
    def slide_up(self):
        self.transpose()
        score = self.slide_left()
        self.transpose()
        return score
    
    def slide_down(self):
        self.transpose()
        score = self.slide_right()
        self.transpose()
        return score
    
    def reflect_horizontal(self):
        self.state = [self.state[r + i] for r in range(0, 16, 4) for i in reversed(range(4))]
        return
    
    def reflect_vertical(self):
        self.state = [self.state[c + i] for c in reversed(range(0, 16, 4)) for i in range(4)]
        return
    
    def transpose(self):
        self.state = [self.state[r + i] for i in range(4) for r in range(0, 16, 4)]
        return
    
    def rotate(self, rot = 1):
        rot = ((rot % 4) + 4) % 4
        if rot == 1:
            self.rotate_right()
            return
        if rot == 2:
            self.reverse()
            return
        if rot == 3:
            self.rotate_left()
            return
        return
    
    def rotate_right(self):
        """ clockwise rotate the board """
        self.transpose()
        self.reflect_horizontal()
        return
    
    def rotate_left(self):
        """ counterclockwise rotate the board """
        self.transpose()
        self.reflect_vertical()
        return
    
    def reverse(self):
        self.reflect_horizontal()
        self.reflect_vertical()
        return
        
    def __str__(self):
        state = '+' + '-' * 24 + '+\n'
        for row in [self.state[r:r + 4] for r in range(0, 16, 4)]:
            state += ('|' + ''.join('{0:6d}'.format(self.constant_table.index2tile(t)) for t in row) + '|\n')
        state += '+' + '-' * 24 + '+'
        return state
    
    
if __name__ == '__main__':
    print('Threes Demo: board.py\n')
    
    state = board()
    state[10] = 10
    print(state)

#!/usr/bin/env python3

"""
Basic framework for developing 2048 programs in Python

Author: Hung Guei (moporgic)
        Computer Games and Intelligence (CGI) Lab, NCTU, Taiwan
        http://www.aigames.nctu.edu.tw
"""

from board import board
from action import action
import random
import numpy as np

class bag:
    def __init__(self):
        self.tile_bag = self._initial_bag()
    
    def choose_tile(self):
        if self.tile_bag == []:
            self.tile_bag = self._initial_bag()
        choose_tile = random.choice(self.tile_bag)
        self.tile_bag.remove(choose_tile)
        return choose_tile

    def _initial_bag(self):
        return [1,2,3]


class agent:
    """ base agent """
    
    def __init__(self, options = ""):
        self.info = {}
        options = "name=unknown role=unknown " + options
        for option in options.split():
            data = option.split("=", 1) + [True]
            self.info[data[0]] = data[1]
        print(self.info)
        return
    
    def open_episode(self, flag = ""):
        return
    
    def close_episode(self, flag = ""):
        return
    
    def take_action(self, state):
        return action()
    
    def check_for_win(self, state):
        return False
    
    def property(self, key):
        return self.info[key] if key in self.info else None
    
    def notify(self, message):
        data = message.split("=", 1) + [True]
        self.info[data[0]] = data[1]
        return
    
    def name(self):
        return self.property("name")
    
    def role(self):
        return self.property("role")


class random_agent(agent):
    """ base agent for agents with random behavior """
    
    def __init__(self, options = ""):
        super().__init__(options)
        seed = self.property("seed")
        if seed is not None:
            random.seed(int(seed))
        self.rstate = random.getstate()
        return
    
    def choice(self, seq):
        random.setstate(self.rstate)
        target = random.choice(seq)
        self.rstate = random.getstate()
        return target
    
    def shuffle(self, seq):
        random.setstate(self.rstate)
        random.shuffle(seq)
        self.rstate = random.getstate()
        return


class rndenv(random_agent):
    """
    random environment
    add a new random tile to an empty cell
    2-tile: 90%
    4-tile: 10%
    """
    
    def __init__(self, options = ""):
        super().__init__("name=random role=environment " + options)
        self.bag = bag()
        
        return
    
    def take_action(self, state, player_slide = None):
        #print(state)
        if player_slide != -1:
            if player_slide == 0:
                empty = [pos for pos, tile in enumerate(state.state) if not tile and pos in [12,13,14,15]]
            elif player_slide == 1:
                empty = [pos for pos, tile in enumerate(state.state) if not tile and pos in [0,4,8,12]]
            elif player_slide == 2:
                empty = [pos for pos, tile in enumerate(state.state) if not tile and pos in [0,1,2,3]]
            elif player_slide == 3:
                empty = [pos for pos, tile in enumerate(state.state) if not tile and pos in [3,7,11,15]]
        
        else:    
            empty = [pos for pos, tile in enumerate(state.state) if not tile]

        if empty:
            #print("player_lastslide ", player_slide)
            #print("position ",empty," bag :",self.bag.tile_bag)
            pos = self.choice(empty)
            tile = self.bag.choose_tile()
            
            return action.place(pos, tile)
        else:
            return action()
    def open_episode(self, flag = ""):
        super().open_episode(flag)
        self.bag.tile_bag = self.bag._initial_bag()
        return 
    
class player(random_agent):
    """
    dummy player
    select a legal action randomly
    """
    
    def __init__(self, options = "name=dummy"):
        super().__init__("name=dummy role=player " + options)
        return
    
    def take_action(self, state):
        if self.info['name'] == 'dummy':
            legal = [op for op in range(4) if board(state).slide(op) != -1]
            if legal:
                op = self.choice(legal)
                return action.slide(op), op
        elif self.info['name'] == 'greedy':
            score_array = [board(state).slide(op) for op in range(4)]
            greedy_op = np.argmax(score_array)
            if score_array[greedy_op] != -1:
                return action.slide(greedy_op), greedy_op
        return action(), -1
    
    
if __name__ == '__main__':
    print('2048 Demo: agent.py\n')
    
    state = board()
    for i in range(4):
        state[4*i+0] = random.randint(1,2)
        state[4*i+1] = random.randint(1,2)
        state[4*i+2] = random.randint(1,2)
        state[4*i+3] = random.randint(1,2)
    print(state)
    env = rndenv()
    ply = player()
    '''
    for i in range(15):
        a = env.take_action(state)
        r = a.apply(state)
        print(a)
        print(r)
        print(state)
    '''
    print("*" * 10)
    
    a, code = ply.take_action(state)
    a.apply(state)
    print(state)
    print(len(state.state))
    #a, code = ply.take_action(state)
    '''
    print(ply.take_action(state))
    print(ply.take_action(state))
    print(ply.take_action(state))
    print(ply.take_action(state))
    print(ply.take_action(state))
    print(ply.take_action(state))
    print(ply.take_action(state))
    print(ply.take_action(state))
    print(ply.take_action(state))
    
    state = board()
    state[0] = 1
    state[1] = 1
    print(state)
    
    print(ply.take_action(state))
    print(ply.take_action(state))
    print(ply.take_action(state))
    print(ply.take_action(state))
    print(ply.take_action(state))
    print(ply.take_action(state))
    print(ply.take_action(state))
    print(ply.take_action(state))
    print(ply.take_action(state))
    print(state)
    '''

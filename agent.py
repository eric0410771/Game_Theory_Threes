#!/usr/bin/env python3

"""
Basic framework for developing 2048 programs in Python

Author: Hung Guei (moporgic)
        Computer Games and Intelligence (CGI) Lab, NCTU, Taiwan
        http://www.aigames.nctu.edu.tw
"""

from board import board
from action import action
from weight import weight
from array import array
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
    
    def update_weight(self, after_states, rewards):
        return 
    
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
    
class weight_agent(random_agent):
    def __init__(self, options = 'name=dummy init=65536', memory_size = 2000):
        super().__init__("name=dummy role=player "+options)
        self.net = []
        self.alpha = 0.1/(4*8)
        self.epsilon = 1.0
        self.train_batch = 50
        self.memory_size = memory_size
        alpha = self.property('alpha')
        self.test = False
        if alpha is not None:
            self.alpha = float(alpha)
        load = self.property('load')
        init = self.property('init')
        if init is not None and load is None:
            self.init_weight(init)
        print("loading from ", load)
        if load is not None:
            self.load_weight(load)
            self.test = True
        train = self.property('train')
        print(train)
        if train is not None:
            self.test = False
        if self.test:
            self.epsilon = 1
        print("net size :",len(self.net[0]))
        return 
    def __exit__(self, exc_type, exc_value, traceback):
        save = self.property('save')
        if save is not None:
            self.save_weight(save)
        return 
    def init_weight(self, init):
        for i in range(len(board.feature_index)):
            self.net += [weight(int(init))]
    def load_weight(self, init):
        input = open(init, 'rb')
        size = array('I')
        size.fromfile(input, 1)
        size = size[0]
        for i in range(size):
            self.net += [weight()]
            self.net[-1].load(input)
        
        return 
    def save_weight(self, path):
        output = open(path, 'wb')
        array('I', [len(self.net)]).tofile(output)

        for w in self.net:
            w.save(output)
        return 
    def update_weight(self, state_index, rewards, after_state_index):
        self.epsilon += 0.0004
        if self.test:
            return
        for i in reversed(range(len(state_index))):
            if rewards[i] == -1:
                delta = self.alpha * (0 - self.sum(state_index[i]))
            else:
                delta = self.alpha * (rewards[i] + self.sum(after_state_index[i]) - self.sum(state_index[i]))
            for j, index in enumerate(state_index[i]):
                self.net[j][index] += delta

        return 
    def get_weight(self):
        return self.net[0]
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
        elif self.info['name'] == 'td_learning':
            if np.random.uniform() < self.epsilon:
                all_values = []
                rewards = []
                for op in range(4):
                    tmp_board = board(state)
                    reward = tmp_board.slide(op)
                    rewards.append(reward)
                    all_values.append(self.sum(tmp_board.features()) + reward)
                
                legal = [op for op in range(4) if rewards[op] != -1]
                if legal:
                    op = legal[np.argmax([all_values[op] for op in legal])]
                    return action.slide(op), op
            else:
                legal = [op for op in range(4) if board(state).slide(op) != -1]
                if legal:
                    op = self.choice(legal)
                    return action.slide(op), op
        return action(), -1

    def sum(self, indices):
        return sum([self.net[i][index] for i,index in enumerate(indices)])


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

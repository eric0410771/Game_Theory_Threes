#!/usr/bin/env python3

"""
Framework for 2048 & 2048-like Games (Python 3)

Author: Hung Guei (moporgic)
        Computer Games and Intelligence (CGI) Lab, NCTU, Taiwan
        http://www.aigames.nctu.edu.tw
"""

from board import board
from action import action
from episode import episode
from statistic import statistic
from agent import player, weight_agent
from agent import rndenv
import sys


if __name__ == '__main__':
    print('Threes Demo: ' + " ".join(sys.argv))
    print()
    
    total, block, limit = 1000, 0, 0
    
    play_args, evil_args = "", ""
    load, save = "", ""
    summary = False
    for para in sys.argv[1:]:
        if "--total=" in para:
            total = int(para[(para.index("=") + 1):])
        elif "--block=" in para:
            block = int(para[(para.index("=") + 1):])
        elif "--limit=" in para:
            limit = int(para[(para.index("=") + 1):])
        elif "--play=" in para:
            play_args = para[(para.index("=") + 1):]
        elif "--evil=" in para:
            evil_args = para[(para.index("=") + 1):]
        elif "--load=" in para:
            load = para[(para.index("=") + 1):]
        elif "--save=" in para:
            save = para[(para.index("=") + 1):]
        elif "--summary" in para:
            summary = True
    
    stat = statistic(total, block, limit)
    
    if load:
        input = open(load, "r")
        stat.load(input)
        input.close()
        summary |= stat.is_finished()
    memory_size = 1000
    print(play_args)
    play = weight_agent(play_args, memory_size = memory_size)
    evil = rndenv(evil_args)

    epoch = 1
    counter = 0
    while not stat.is_finished():
        if epoch % 50 == 0:
            print("Current epoch ",epoch)
        epoch += 1
        state_index = []
        after_state_index = []
        rewards = []

        play.open_episode("~:" + evil.name())
        evil.open_episode(play.name() + ":~")
        
        stat.open_episode(play.name() + ":" + evil.name())
        game = stat.back()
        player_lastslide = -1
        state = None
        while True:
            who = game.take_turns(play, evil)
            if who.info['role'] == "player":
                move, slide_direction = who.take_action(game.state())
                player_lastslide = slide_direction
            else:
                move = who.take_action(game.state(), player_lastslide)
            
            legal_action ,reward = game.apply_action(move)
            if who.info['role'] == 'player':
                if state == None:
                    state = game.state().features()
                else:
                    state_index.append(state)
                    after_state_index.append(game.state().features())
                    rewards.append(reward)
                    state = after_state_index[-1]

            if not legal_action or who.check_for_win(game.state()):
                break

        win = game.last_turns(play, evil)
        stat.close_episode(win.name())
        
        play.close_episode(win.name())
        play.update_weight(state_index, rewards, after_state_index)

        evil.close_episode(win.name())
    play.save_weight('weight.bin')
    if summary:
        stat.summary()
    if save:
        output = open(save, "w")
        stat.save(output)
        output.close()
    
        

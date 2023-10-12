#!/usr/bin/env python3

import numpy as np
import random
from collections import defaultdict

from players import Player, PlayerRandom, PlayerAttack
import model

from arena import Arena

class QLearning:
    def __init__(self):
        actions = [0, 1]
        self.actions = actions
        self.learning_rate = 0.01
        self.discount_factor = 0.9
        self.epsilon = 0.1
        self.q_table = defaultdict(lambda: [0.0, 0.0])

    # update q function with sample <s, a, r, s'>
    def learn(self, state, action, reward, next_state):
        current_q = self.q_table[state][action]
        # using Bellman Optimality Equation to update q function
        new_q = reward + self.discount_factor * max(self.q_table[next_state])
        self.q_table[state][action] += self.learning_rate * (new_q - current_q)

    # get action for the state according to the q function table
    # agent pick action of epsilon-greedy policy
    def get_action(self, state):
        if np.random.rand() < self.epsilon:
            # take random action
            action = np.random.choice(self.actions)
        else:
            # take action according to the q function table
            state_actions = self.q_table[state]
            action = self.arg_max(state_actions)
        return action

    @staticmethod
    def arg_max(state_actions):
        max_index_list = []
        max_value = state_actions[0]
        for index, value in enumerate(state_actions):
            if value > max_value:
                max_index_list.clear()
                max_value = value
                max_index_list.append(index)
            elif value == max_value:
                max_index_list.append(index)
        return random.choice(max_index_list)
    
    def print(self):
        for key,value in sorted(self.q_table.items()):
            print(key,value)

    def step(self, state, action, reward, next_state):
        if state is not None:
            # take action and proceed one step in the environment
            # with sample <s,a,r,s'>, agent learns new q function
            self.learn(state, action, reward, next_state)
        return self.get_action(next_state)


q = QLearning()


class QAgent(Player):
    def __init__(self):
        self.qstate = None
        self.qaction = None

    @staticmethod
    def state(game):
        axis = game.axis
        allies = game.allies
        return str(allies.unit.figures)+'/'+str(axis.unit.figures)

    def select(self, game, actions):
        next_state = self.state(game)
        reward = self.reward(game)
        self.qaction = q.step(self.qstate, self.qaction, reward, next_state)
        self.qstate = next_state
        return model.Action.NONE if self.qaction==0 else model.Action.ATTACK

    def reward(self, game):
        # allies lost
        if game.allies.unit.figures==0:
            return -100
        # axis lost
        if game.axis.unit.figures==0:
            return 100
        return 0

    def end(self, game):
        #print('I loose')
        next_state = self.state(game)
        reward = self.reward(game)
        q.step(self.qstate, self.qaction, reward, next_state)


if __name__ == "__main__":
    players = [
          QAgent()
        , PlayerAttack() ]
    arena = Arena()
    arena.play(players, 1000)
    q.print()

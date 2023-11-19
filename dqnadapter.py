#!/usr/bin/env python3

import numpy as np

import model


class ActionAdapter:
    action_size = len(model.Action.All)
    @staticmethod
    def str(qactions):
        return ','.join([ f'{a:+5.1f}' for a in qactions[0]])
    @staticmethod
    def to_qactions(actions):
        # convert actions to index
        return [ model.Action.All.index(action) for action in actions ]
    @staticmethod
    def from_qaction(qaction):
        return model.Action.All[qaction]


class StateAdapter:
    @staticmethod
    def to_np(s):
        s = np.asarray(s)
        return s.reshape((1, StateAdapterCurrent.state_size))
    @staticmethod
    def state(game):
        # convert game to np state
        pass

class StateAdapterCoord:
    state_size = 7
    # state contains unit coords
    @staticmethod
    def state(game):
        axis = game.axis
        allies = game.allies
        state = ( game.phase
                , allies.unit.position.x, allies.unit.position.y, allies.unit.figures
                , axis.unit.position.x, axis.unit.position.y, axis.unit.figures
                )
        return StateAdapter.to_np(state)

class StateAdapterPos:
    # state contains a map x,y with unit inside
    # phase
    # map 4*5 (don't lind for out bound hexs)
    # with unit number 0: empty, +n: allies, -n: axies
    state_size = 1+4*5
    @staticmethod
    def state(game):
        axis = game.axis.unit
        allies = game.allies.unit
        board = [0]*4*5
        allies_index = allies.position.x + allies.position.y*4
        axis_index = axis.position.x + axis.position.y*4
        board[allies_index] = allies.figures
        board[axis_index] = -axis.figures
        state = [ game.phase ] + board
        return StateAdapter.to_np(state)

StateAdapterCurrent = StateAdapterCoord
#StateAdapterCurrent = StateAdapterPos


class Rewarder:
    def reward(self, game):
        # Evaluate game reward
        pass

class RewarderEnd(Rewarder):
    # Reward only at game end
    def reward(self, game):
        # allies lost
        if game.allies.unit.figures==0:
            #return 10
            return -10
        # axis lost
        if game.axis.unit.figures==0:
            #return 20
            return 10
        #return 15
        return 0

class RewarderEndAttack(RewarderEnd):
    def __init__(self):
        # delta figures
        self.delta = 0
    # Reward at game end and successful attacks
    def reward(self, game):
        allies = game.allies.unit.figures
        # allies lost
        if allies==0:
            return -10
        # axis lost
        axis = game.axis.unit.figures
        if axis==0:
            return 10
        delta = allies - axis
        score = delta - self.delta
        self.delta = delta
        return score

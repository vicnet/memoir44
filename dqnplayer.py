#!/usr/bin/env python3

import os

import numpy as np

from dqnmodel import DQNModel

from dqnadapter import ActionAdapter, StateAdapterCurrent
from players import Player


class DQNPlayer(Player):
    def __init__(self, qmodel=None):
        self.q = qmodel
        if self.q is None:
            self.q = DQNModel(state_size=StateAdapterCurrent.state_size, action_size=ActionAdapter.action_size)
            weights_filename = 'dqn.weights'
            if os.path.isfile(weights_filename+'.index'):
                self.q.load(weights_filename)

    def select(self, game, actions):
        # convert actions to index
        qactions = ActionAdapter.to_qactions(actions)
        # get information
        state = StateAdapterCurrent.state(game)
        qaction = self.q.act(state, qactions)
        return ActionAdapter.from_qaction(qaction)

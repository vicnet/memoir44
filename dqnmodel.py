#!/usr/bin/env python3

import os
import numpy as np

from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from keras.metrics import Accuracy
import keras


class DQNModel:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.model = self.build_model()

    def build_model(self):
        # Neural Net for Deep-Q learning Model
        model = Sequential()
        nb_neurons = 24
        #nb_neurons = 8
        model.add(Dense(nb_neurons, input_dim=self.state_size, activation='relu'))
        model.add(Dense(nb_neurons, activation='relu'))
        model.add(Dense(self.action_size, activation='linear', kernel_initializer=keras.initializers.RandomNormal(mean=-15)))
        return model

    def predict(self, state):
        return self.model.predict(state, verbose=0)

    def act(self, state, actions):
        """actions are available action indexes."""
        # use NN to get actions rewards
        act_values = self.predict(state)
        # selection available action in actions
        sorted_actions = np.argsort(act_values[0])
        for action in reversed(sorted_actions):
            if action in actions:
                return action
        return 0

    def load(self, name):
        self.model.load_weights(name).expect_partial()
        with open(name+'.metaparam') as f:
            self.epsilon = float(f.read())

    def save(self, name):
        self.model.save_weights(name, overwrite=True)
        with open(name+'.metaparam', mode='w') as f:
            f.write(str(self.epsilon))

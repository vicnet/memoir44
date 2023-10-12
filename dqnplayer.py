#!/usr/bin/env python3

import numpy as np
import random

import numpy as np
from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam

from players import Player, PlayerRandom, PlayerAttack
import model

from arena import Arena


class DQNLearning:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95    # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()

    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = Sequential()
        model.add(Dense(24, input_dim=self.state_size, activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse',
                      optimizer=Adam(learning_rate=self.learning_rate))
        return model

    def memorize(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def predict(self, state):
        return self.model.predict(state, verbose=0)

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        act_values = self.model.predict(state, verbose=0)
        return np.argmax(act_values[0])  # returns action

    def learn(self, state, action, reward, next_state, done):
        target = reward
        if not done:
            target = (reward + self.gamma *
                        np.amax(self.model.predict(next_state, verbose=0)[0]))
        target_f = self.model.predict(state, verbose=0)
        target_f[0][action] = target
        self.model.fit(state, target_f, epochs=1, verbose=0)

    def replay(self, batch_size):
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            self.learn(state, action, reward, next_state, done)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)

    def print(self):
        pass

    def step(self, state, action, reward, next_state, done):
        if state is not None:
            # take action and proceed one step in the environment
            # with sample <s,a,r,s'>, agent learns new q function
            self.learn(state, action, reward, next_state, done)
        return self.act(next_state)


q = DQNLearning(2,2)


class DQNAgent(Player):
    def __init__(self):
        self.qstate = None
        self.qaction = None

    @staticmethod
    def to_np(s):
        s = np.asarray(s)
        return s.reshape((1,2))

    @staticmethod
    def state(game):
        axis = game.axis
        allies = game.allies
        return DQNAgent.to_np((allies.unit.figures,axis.unit.figures))

    def select(self, game, actions):
        next_state = self.state(game)
        reward = self.reward(game)
        self.qaction = q.step(self.qstate, self.qaction, reward, next_state, False)
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
        q.step(self.qstate, self.qaction, reward, next_state, True)
    
    def print(self):
        for i in range(4):
            for j in range(4):
                s = DQNAgent.to_np((i,j))
                print(s, q.predict(s))


if __name__ == "__main__":
    players = [
          DQNAgent()
        , PlayerAttack() ]
    arena = Arena()
    arena.play(players, 10)
    players[0].print()

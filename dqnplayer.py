#!/usr/bin/env python3

import os
import numpy as np
import random
from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from keras.metrics import Accuracy
import keras

import model
from players import Player
from observer import Follow, ScoresTxt, ScoresPlot, ScoresStopper


class DQNLearning:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        # deque with maxlen: forget old values
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95    # discount rate
        self.epsilon = 1  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()
        # paramters for replays
        self.state_count = 0
        self.batch_size = 10 #32
        self.learn_period = 10
        # parameters to see convergence ?
        self.metrics = []

    def play_only(self):
        self.epsilon = 0  # not exploration, use q table
        self.epsilon_min = 0.0
        self.epsilon_decay = 1

    def reset(self):
        self.model = self._build_model()
        self.epsilon = 1

    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = Sequential()
        #nb_neurons = 24
        nb_neurons = 8
        model.add(Dense(nb_neurons, input_dim=self.state_size, activation='relu'))
        model.add(Dense(nb_neurons, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse'
                    #loss=masked_huber_loss(0.0, 1.0)
                    , optimizer=Adam(learning_rate=self.learning_rate)
                    #, metrics=[Accuracy()]
                    )
        #model.summary()
        #keras.utils.plot_model(model)
        return model

    def memorize(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def predict(self, state):
        return self.model.predict(state, verbose=0)

    def act(self, state, actions):
        """Actions are available action indexes."""
        # random depends on epsilon
        if np.random.rand() <= self.epsilon:
            return random.choice(actions)
        # use NN to get actions rewards
        act_values = self.predict(state)
        # selection available action in actions
        sorted_actions = np.argsort(act_values[0])
        for action in reversed(sorted_actions):
            if action in actions:
                return action
        return 0

    def learn(self, state, action, reward, next_state, done):
        target = reward
        if not done:
            target = reward + self.gamma * np.amax(self.predict(next_state)[0])
        target_f = self.predict(state)
        #print('state', state[0], 'give', [ f'{a:.2}' for a in target_f[0]],'for action', action, ' and reward', reward, ' target', target)
        #print('state', state[0], 'give', target_f[0][0],'for action', action, ' and reward', reward, ' target', target)
        target_f[0][action] = target
        #print('fit  ', state[0], 'to  ', target_f[0][0])
        #self.model.fit(state, target_f, epochs=1, verbose=0)
        res = self.model.fit(state, target_f, epochs=1, verbose=0)
        self.metrics.append([h[0] for h in res.history.values()])

    def replay(self, batch_size):
        batch_size = min(batch_size, len(self.memory))
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            self.learn(state, action, reward, next_state, done)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def load(self, name):
        self.model.load_weights(name).expect_partial()
        with open(name+'.metaparam') as f:
            self.epsilon = float(f.read())

    def save(self, name):
        self.model.save_weights(name, overwrite=True)
        with open(name+'.metaparam', mode='w') as f:
            f.write(str(self.epsilon))
        #import csv
        #with open(name+'.metrics.csv', 'w') as f:
            #csv_writer = csv.writer(f)
            #csv_writer.writerow(['Loss', 'Accuracy'])
            #csv_writer.writerows(self.metrics)

    def step(self, state, action, reward, next_state, done, actions=[0]):
        if state is not None:
            # take action and proceed one step in the environment
            # with sample <s,a,r,s'>, agent learns new q function
            #print(state, action, reward, next_state, done)
            self.memorize(state, action, reward, next_state, done)
            self.state_count += 1
            if self.state_count%self.learn_period==0:
                self.replay(self.batch_size)
        return self.act(next_state, actions)


class Stater:
    @staticmethod
    def to_np(s):
        s = np.asarray(s)
        return s.reshape((1, StaterCurrent.state_size))
    @staticmethod
    def state(game):
        # convert game to np state
        pass

class StaterCoord:
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
        return Stater.to_np(state)

class StaterPos:
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
        return Stater.to_np(state)

StaterCurrent = StaterCoord
#StaterCurrent = StaterPos

class Rewarder:
    @staticmethod
    def reward(game):
        # Evaluate game reward
        pass

class RewarderEnd:
    # Reward only at game end
    @staticmethod
    def reward(game):
        # allies lost
        if game.allies.unit.figures==0:
            return -10
        # axis lost
        if game.axis.unit.figures==0:
            return 10
        return 0


class DQNPlayer(Player):
    def __init__(self, learn=False):
        self.qstate = None
        self.qaction = None
        self.learn = learn
        self.state = StaterCurrent.state
        self.reward = RewarderEnd.reward
        if not self.learn:
            q.play_only()

    @staticmethod
    def to_qactions(actions):
        # convert actions to index
        return [ model.Action.All.index(action) for action in actions ]

    @staticmethod
    def from_qaction(qaction):
        return model.Action.All[qaction]

    def select(self, game, actions):
        # convert actions to index
        qactions = self.to_qactions(actions)
        # get information
        next_state = self.state(game)
        reward = self.reward(game)
        self.qaction = q.step(self.qstate, self.qaction, reward, next_state, False, qactions)
        if self.learn:
            self.qstate = next_state
        return self.from_qaction(self.qaction)

    def end(self, game):
        next_state = self.state(game)
        reward = self.reward(game)
        # TODO revoir l'utilisation de memory
        q.step(self.qstate, self.qaction, reward, next_state, True)
    


q = DQNLearning(state_size=StaterCurrent.state_size, action_size = len(model.Action.All))
weights_filename = 'dqn.weights'
if os.path.isfile(weights_filename+'.index'):
    q.load(weights_filename)


if __name__ == "__main__":
    import sys
    from arena import Arena
    from observer import Observer, MultiObserver
    import logging
    from log import LoggingColor, progress
    from players import *
    import matplotlib.pyplot as plt

    def learn():
        class Plot(Observer):
            def __init__(self):
                plt.ion()
            def end(self, game, winner_num, winner_player):
                plt.clf()
                plt.plot(q.metrics)
                plt.draw()
                plt.pause(0.01)
                return False
            def end_contest(self):
                plt.ioff()
                plt.clf()
                plt.plot(q.metrics)
                plt.show()

        # rebuild model from scratch
        q.reset()
        # now learn
        opponents = []
        opponents.append(PlayerRandom())
        #opponents.append(PlayerTracker())
        #opponents.append(DQNPlayer(learn=True))
        for opponent in opponents:
            players = [
                DQNPlayer(learn=True)
                , opponent
                ]
            count = 50
            #arena = Arena(Plot())
            arena = Arena(Follow())
            arena.play(players, count)
            print()
            #players[0].print()
        q.save(weights_filename)

    def play():
        class Debug(Observer):
            #def start(self, game):
                #state = DQNPlayer.state(game)
                #print(state, q.predict(state))
            def turn(self, game):
                if game.phase==model.Phase.ATTACK:
                    state = DQNPlayer.state(game)
                    qvalues = q.predict(state)[0]
                    print(state, qvalues[0], qvalues[1])

        LoggingColor.configure(logging.DEBUG)

        arena = Arena(Debug())
        arena.play([
            DQNPlayer(),
            PlayerRandom()
        ], 1)
    
    def test():
        class Memorize(Observer):
            def __init__(self):
                super().__init__()
                self.state = StaterCurrent.state
                self.reward = RewarderEnd.reward
                self.memory = []
            def selected(self, game, action):
                if game.current!=0: return
                qactions = DQNPlayer.to_qactions([action])
                store = (self.state(game), qactions[0], None)
                self.memory.append(store)
            def played(self, game):
                if game.current!=0: return
                self.memorize(game)
            def memorize(self, game):
                state, action, reward = self.memory[-1]
                reward = self.reward(game)
                self.memory[-1] = (state, action, reward)
            def end(self, game, winner_num, winner_player):
                if game.current!=0:
                    self.memorize(game)
                # propate rewards
                current_reward = 0
                gamma = 0.8
                for index in range(len(self.memory)-1,-1,-1):
                    state,qaction,reward = self.memory[index]
                    current_reward = reward + current_reward*gamma
                    self.memory[index] = (state, qaction, current_reward)
                # display rewards
                #self.display()
                # memorize in nn
                for index in range(len(self.memory)):
                    state,qaction,reward = self.memory[index]
                    q.memorize(state, qaction, reward, None, True)
                q.replay(32)
                if self.count%10==1: self.display()
                self.memory = []
                #progress(self.count, self.total)
                return False
            def display(self):
                # display rewards
                for state,qaction,reward in self.memory:
                    if state[0][0]!=1: continue
                    action = DQNPlayer.from_qaction(qaction)
                    predicts = q.predict(state)
                    print(f'{state[0]} {str(action):<16s} {reward:<10.2} {predicts[0][qaction]:<10.2}')
                print()

        # rebuild model from scratch
        q.reset()
        observers = MultiObserver([
            Memorize(), ScoresTxt(10), ScoresPlot(15),
            ScoresStopper(30)
            ])
        #observers = Memorize()
        arena = Arena(observers)
        arena.play([
            DQNPlayer(),
            #PlayerRandom(),
            PlayerTracker()
            #PlayerRandom(),
        ], 100)
        print()
        q.save(weights_filename)

    #learn()
    #play()
    test()

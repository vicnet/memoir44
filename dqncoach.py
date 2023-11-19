#!/usr/bin/env python3

import numpy as np
import random
from collections import deque

from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
#from keras.metrics import Accuracy

from dqnmodel import DQNModel
from dqnadapter import StateAdapterCurrent, ActionAdapter, RewarderEnd, RewarderEndAttack
from dqnplayer import DQNPlayer

from players import *
from observer import Observer, MultiObserver, ScoresTxt, ScoresPlot
from arena import Arena


class DQNLearning(DQNModel):
    def __init__(self, state_size, action_size):
        super().__init__(state_size, action_size)
        # deque with maxlen: forget old values
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95    # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.compile_model()
        #self.metrics = []

    def compile_model(self):
        self.model.compile(loss='mse'
                    #loss=masked_huber_loss(0.0, 1.0)
                    , optimizer=Adam(learning_rate=self.learning_rate)
                    #, metrics=[Accuracy()]
                    )
        #self.model.summary()
        #keras.utils.plot_model(self.model)

    def memorize(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state, actions):
        """actions are available action indexes."""
        # random depends on epsilon
        if np.random.rand() <= self.epsilon:
            return random.choice(actions)
        return super().act(state, actions)

    def learn(self, state, action, reward, next_state, done):
        target = reward
        snext_target = ' '*60
        if not done:
            next_target = self.predict(next_state)
            snext_target = ActionAdapter.str(next_target)
            target = reward + self.gamma * np.amax(next_target[0])
        target_f = self.predict(state)
        starget_f = ActionAdapter.str(target_f)
        #print('state', state[0], 'give', [ f'{a:.2}' for a in target_f[0]],'for action', action, ' and reward', reward, ' target', target)
        #print('state', state[0], 'give', target_f[0][0],'for action', action, ' and reward', reward, ' target', target)
        target_f[0][action] = target
        #print('fit  ', state[0], 'to  ', target_f[0][0])
        self.model.fit(state, target_f, epochs=1, verbose=0)
        #self.metrics.append([h[0] for h in res.history.values()])
        #print(state[0], f'{reward:+5.1f}', f'{target:+5.1f} /', next_state, '-', snext_target, '|', starget_f,'|', ActionAdapter.str(target_f))

    def replay(self, batch_size):
        batch_size = min(batch_size, len(self.memory))
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            self.learn(state, action, reward, next_state, done)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay


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


class Memorize(Observer):
    def __init__(self):
        super().__init__()
        self.state = StateAdapterCurrent.state
        self.rewarder = RewarderEndAttack()
        # use q netword propagation
        self.qpropagate = True
        #self.qpropagate = False
        # factor for reward propagation
        # (first actions less participate to the rewards)
        #self.gamma = None
        self.gamma = 0.8
        # one game memory
        self.memory = []

    def selected(self, game, action):
        if game.current!=0: return
        qactions = ActionAdapter.to_qactions([action])
        store = (self.state(game), qactions[0], None)
        self.memory.append(store)

    def played(self, game):
        if game.current!=0: return
        self.memorize(game)

    def memorize(self, game):
        state, action, _ = self.memory[-1]
        reward = self.rewarder.reward(game)
        self.memory[-1] = (state, action, reward)

    def propage_rewards(self):
        current_reward = 0
        # reverse loop: propage from to begining with decay factor
        for index in range(len(self.memory)-1,-1,-1):
            state,qaction,reward = self.memory[index]
            current_reward = reward + (current_reward * self.gamma)
            self.memory[index] = (state, qaction, current_reward)

    def transfert_to_qnetwork(self):
        size = len(self.memory)
        for index in range(size):
            state,qaction,reward = self.memory[index]
            if not self.qpropagate or index==size-1:
                # if use internal reward propagation,
                # always set done = true in q network.
                # That stop the q network propagation
                done = True
                next_state = None
            else:
                done = False
                next_state,_,_ = self.memory[index+1]
            q.memorize(state, qaction, reward, next_state, done)
        self.memory = []

    def end(self, game, winner_num, winner_player):
        if game.current!=0:
            self.memorize(game)
        # propate rewards
        if self.gamma:
            self.propage_rewards()
        if self.count%10==1: self.display_rewards()
        # memorize game steps in neural network
        self.transfert_to_qnetwork()
        q.replay(32)
        return False

    #def start(self, game):
        #super().start(game)
        #if self.count%10==1:
            #state = self.state(game)
            #qvalues = q.predict(state)[0]
            #print()
            #print(state, qvalues)

    def display_rewards(self):
        # display actions and rewards from the current game
        for state,qaction,reward in self.memory:
            if state[0][0]!=1: continue # only display attack phase
            action = ActionAdapter.from_qaction(qaction)
            predicts = q.predict(state)
            print(f'{state[0]} {str(action):<16s} {float(reward):<10.2f} {predicts[0][qaction]:<10.2f}')
        print()


q = DQNLearning(state_size=StateAdapterCurrent.state_size, action_size = ActionAdapter.action_size)
weights_filename = 'dqn.weights'

observers = MultiObserver([
    Memorize(),
    ScoresTxt(10), ScoresPlot(15),
    #ScoresStopper(30)
    ])
#observers = Memorize()
arena = Arena(observers)
arena.play([
    DQNPlayer(q),
    PlayerRandom(),
    #PlayerTracker()
    #PlayerRandom(),
], 100)
print()
q.save(weights_filename)
print(q.epsilon)

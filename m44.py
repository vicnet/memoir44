#!/usr/bin/env python3

import random

import model
import gui


class Player:
    pass

class PlayerAttack(Player):
    """Always attack"""
    def play(self, game, actions):
        return actions[1]

class PlayerRandom(Player):
    """Always attack"""
    def play(self, game, actions):
        return random.choice(actions)

class PlayerPacific(Player):
    """Always attack"""
    def play(self, game, actions):
        return actions[0]


game = model.Game()

thread = gui.ThreadApp(game)

#allies = PlayerAttack()
allies = PlayerRandom()
#allies = PlayerPacific()
axis = PlayerRandom()

import time
print('start game')
while True:
    print('start turn')
    actions = game.actions()
    if game.current==model.Player.Side.ALLIES:
        current = allies
    else:
        current = axis
    action = current.play(game, actions)
    game.play(action)
    thread.update()
    if game.end(): break
    print('end turn')
    time.sleep(1)
    game.switch()

print('end game')

#import time
#time.sleep(1)
#thread.update()

#print("player 1")
#action = input()
thread.join()

#!/usr/bin/env python3

import random

class Player:
    def select(self, game, actions):
        return None

    def play(self, game, actions):
        action = self.select(game, actions)
        game.play(action)

    def win(self, game):
        self.end(game)

    def loose(self, game):
        self.end(game)

    def end(self, game):
        pass


class PlayerAttack(Player):
    """Always attack"""
    def select(self, game, actions):
        return actions[1]

class PlayerRandom(Player):
    """Always attack"""
    def select(self, game, actions):
        return random.choice(actions)

class PlayerPacific(Player):
    """Always attack"""
    def select(self, game, actions):
        return actions[0]

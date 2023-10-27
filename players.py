#!/usr/bin/env python3

import random
import model

class Player:
    def select(self, game, actions):
        return None

    def win(self, game):
        self.end(game)

    def loose(self, game):
        self.end(game)

    def end(self, game):
        pass


class PlayerAttack(Player):
    """Always attack. No move"""
    def select(self, game, actions):
        if game.phase!=model.Phase.ATTACK:
            return actions[0]
        if len(actions)<=1:
            return actions[0]
        return actions[1]

class PlayerRandom(Player):
    """Always attack"""
    def select(self, game, actions):
        return random.choice(actions)

class PlayerPacific(Player):
    """Always attack"""
    def select(self, game, actions):
        return actions[0]

class PlayerTracker(PlayerAttack):
    """Move to opponent. Always attack if possible."""
    def select(self, game, actions):
        if game.phase==model.Phase.ATTACK:
            return super().select(game, actions)
        # MOVE phase
        player = game.player().unit.position
        aimed = game.opponent().unit.position
        dist = player.distance(aimed)
        if dist==1:
            return actions[0]
        mins = [ ]
        for action in actions[1:]:
            direction = action.direction
            pos = player.copy()
            pos.move(direction)
            if pos.distance(aimed)==dist-1:
                mins.append(action)
        if len(mins)==0:
            return actions[0]
        return random.choice(mins)

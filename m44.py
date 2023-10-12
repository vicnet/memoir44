#!/usr/bin/env python3

from arena import Arena, Callback
from players import *


class Scores(Callback):
    def __init__(self):
        self.scores = [0, 0]

    def end(self, game, winner_num, winner_player):
        self.scores[winner_num] += 1

    def __str__(self):
        return str(self.scores)


scores = Scores()

#PlayerAttack()
#PlayerPacific()

arena = Arena(scores)
arena.play([PlayerAttack(), PlayerRandom()], 10000)

print(scores)

#!/usr/bin/env python3

from arena import Arena, Callback
from players import *


class Scores(Callback):
    def __init__(self):
        self.scores = [0, 0]

    def end(self, game, winner_num, winner_player):
        self.scores[winner_num] += 1

    def __str__(self):
        total = sum(self.scores)
        percent = [ int(value/total*100) for value in self.scores ]
        return f'{self.scores}  ({percent[0]}%/{percent[1]}%)'


scores = Scores()

#PlayerAttack()
#PlayerPacific()

arena = Arena(scores)
arena.play([PlayerTracker(), PlayerAttack()], 5000)

print(scores)

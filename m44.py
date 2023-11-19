#!/usr/bin/env python3

from arena import Arena
from observer import ScoresTxt, ScoresPlot, MultiObserver
from players import *
from dqnplayer import DQNPlayer
import log

import logging
from log import LoggingColor

#LoggingColor.configure(logging.DEBUG)

#PlayerAttack()
#PlayerPacific()

count = 100
observer = MultiObserver([ScoresTxt(), ScoresPlot(15)])
#observer = ScoresTxt()
arena = Arena(observer)
arena.play([
    DQNPlayer(),
    #DQNPlayer(),
    #PlayerRandom(),
    #PlayerRandom(),
    PlayerTracker(),
    #PlayerTracker(),
    ], count)
print()

#!/usr/bin/env python3

import log
import matplotlib.pyplot as plt


class Observer:
    def __init__(self):
        self.count = 0
        self.total = 0
    def start(self, game):
        # start game
        self.count += 1
    def end(self, game, winner_num, winner_player):
        # end game, return True to stop fighting
        return False
    def selected(self, game, action):
        # action choosen
        pass
    def played(self, game):
        # action played on game
        pass
    def turn(self, game):
        # end turn
        pass
    def start_contest(self, total):
        self.total = total
    def end_contest(self):
        pass


class MultiObserver(Observer):
    def __init__(self, observers=[]):
        super().__init__()
        self.observers = observers
    def add(self, observer):
        self.observers.append(observer)
        return self
    def start(self, game):
        super().start(game)
        for observer in self.observers:
            observer.start(game)
    def end(self, game, winner_num, winner_player):
        end = False
        for observer in self.observers:
            if observer.end(game, winner_num, winner_player):
                end = True
        return end
    def selected(self, game, action):
        for observer in self.observers:
            observer.selected(game, action)
    def played(self, game):
        for observer in self.observers:
            observer.played(game)
    def turn(self, game):
        for observer in self.observers:
            observer.turn(game)
    def start_contest(self, total):
        for observer in self.observers:
            observer.start_contest(total)
    def end_contest(self):
        for observer in self.observers:
            observer.end_contest()


class Scores(Observer):
    def __init__(self, keep=None):
        super().__init__()
        self.scores = []
        self.keep = keep

    def end(self, game, winner_num, winner_player):
        self.scores.append(int(winner_num))
        if self.keep is not None:
            self.scores = self.scores[-self.keep:]
        return self.display()
    
    def percent(self):
        scores = (self.scores.count(0), self.scores.count(1))
        total = len(self.scores)
        return [ int(value/total*100) for value in scores ]
    
    def display(self):
        return False

class ScoresTxt(Scores):
    def __init__(self, keep=None):
        super().__init__(keep)

    def display(self):
        log.progress(self.count, self.total, suffix=str(self))
        return False

    def __str__(self):
        scores = (self.scores.count(0), self.scores.count(1))
        percent = self.percent()
        return f'{scores}  ({percent[0]:3}%/{percent[1]:3}%)'

class ScoresPlot(Scores):
    def __init__(self, keep=None):
        super().__init__(keep)
        self.percents = []
        plt.ion()
    def display(self):
        plt.clf()
        percents = self.percent()
        self.percents.append(percents[0])
        plt.ylim(0, 100)
        plt.axhline(y=50, linestyle='--', color='red', label='Ligne médiane')
        plt.plot(self.percents)
        plt.draw()
        plt.pause(0.01)
        return False
    def end_contest(self):
        plt.ioff()
        self.display()
        plt.show()

class ScoresStopper(Scores):
    def __init__(self, keep=None):
        super().__init__(keep)
    def display(self):
        # we stop if allies always win in keeped scores
        # only if at least keep samples
        if len(self.scores)<self.keep:
            return False
        return self.scores.count(1)==0


class Follow(Observer):
    def start_contest(self, total):
        super().start_contest(total)
        progress(0, self.total)
    def end(self, game, winner_num, winner_player):
        progress(self.count, self.total)
        return False

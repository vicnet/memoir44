#!/usr/bin/env python3

import model
from observer import Observer


class Arena:
    def __init__(self, observer=None):
        if observer is None:
            self.observer = Observer
        else:
            self.observer = observer

    def play_once(self, players):
        game = model.Game()
        self.observer.start(game)
        while True:
            actions = game.actions()
            current = players[game.current]
            # play and get last action
            action = current.select(game, actions)
            self.observer.selected(game, action)
            game.play(action)
            self.observer.played(game)
            if game.end():
                break
            game.next()
            self.observer.turn(game)
        winner = game.winner()
        players[winner].win(game)
        oponnent = (winner+1)%2
        players[oponnent].loose(game)
        return self.observer.end(game, winner, players[winner])

    def play(self, players, nbtime=1):
        self.observer.start_contest(nbtime)
        for episode in range(nbtime):
            if self.play_once(players):
                print('Stop earlier')
                break
        self.observer.end_contest()

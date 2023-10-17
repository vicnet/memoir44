#!/usr/bin/env python3

import model

class Callback:
    def start(self, game):
        pass
    def end(self, game, winner_num, winner_player):
        pass
    def turn(self, game):
        pass

class Arena:
    def __init__(self, callback=None):
        self.callback = callback

    def play_once(self, players):
        game = model.Game()
        if self.callback is not None:
            self.callback.start(game)
        while True:
            actions = game.actions()
            current = players[game.current]
            current.play(game, actions)
            if game.end():
                break
            if self.callback is not None:
                self.callback.turn(game)
        winner = game.winner()
        players[winner].win(game)
        oponnent = (winner+1)%2
        players[oponnent].loose(game)
        if self.callback is not None:
            self.callback.end(game, winner, players[winner])
    
    def play(self, players, nbtime=1):
        for episode in range(nbtime):
            self.play_once(players)

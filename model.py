#!/usr/bin/env python3

from enum import Enum, IntEnum
import random


class Coord:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height

class Unit:
    def __init__(self, figures):
        # number of figures
        self.figures = figures
        self.position = None


class Infantry(Unit):
    def __init__(self):
        super().__init__(4)
    def kill(self):
        if self.figures>0:
            self.figures -= 1


class State:
    pass


class Dice:
    class Face(Enum):
        INFANTERY = 0,
        GRENADE = 1,
        TANK = 2,
        FLAG = 3,
        STAR = 4
        
    Faces = [ Face.INFANTERY
            , Face.INFANTERY
            , Face.GRENADE
            , Face.TANK
            , Face.FLAG
            , Face.STAR ]


class Action:
    @classmethod
    def Init(cls):
        cls.NONE = ActionNone()
        cls.ATTACK = ActionAttack()

    def playOn(self, game):
        pass

class ActionNone(Action):
    def playOn(self, game):
        pass

class ActionAttack(Action):
    def playOn(self, game):
        other = (game.current+1)%2
        aimed = game.players[other].unit
        for _ in range(3):
            dice = random.choice(Dice.Faces)
            if dice==Dice.Face.INFANTERY or dice==Dice.Face.GRENADE:
                self.kill(aimed)
        if aimed.figures==0:
            game.players[game.current].medals += 1

    def kill(self, aimed):
        print('killed')
        aimed.kill()

class Player:
    class Side(IntEnum):
        ALLIES = 0
        AXES = 1

    def __init__(self, side):
        self.side = side
        self.unit = Infantry()
        self.medals = 0


class Game:
    def __init__(self):
        self.board = Board(4,5)
        self.allies = Player(Player.Side.ALLIES)
        self.allies.unit.position = Coord(1,1)
        self.axis = Player(Player.Side.AXES)
        self.axis.unit.position = Coord(2,2)
        
        self.players = [ self.allies, self.axis ]
        self.current = Player.Side.ALLIES
        
        Action.Init()

    def actions(self):
        return [ Action.NONE, Action.ATTACK ]

    def play(self, action):
        action.playOn(self)

    def end(self):
        for player in self.players:
            if player.medals>=1:
                return True
        return False

    def switch(self):
        """Switch player."""
        self.current = (self.current+1)%2

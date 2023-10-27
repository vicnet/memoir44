#!/usr/bin/env python3

from enum import Enum, IntEnum
import random
import warnings
import logging as log


class Coord:
    class Move:
        UP_EAST = ((0,-1), (1,-1),  'Up East')
        UP_WEST = ((-1,-1), (0,-1), 'Up West')
        EAST = ((1,0), (1,0),       'East')
        WEST = ((-1,0), (-1,0),     'West')
        DOWN_EAST = ((0,1), (1,1),  'Down East')
        DOWN_WEST = ((-1,1), (0,+1), 'Down West')

    def __init__(self, x, y):
        self.x = x
        self.y = y
    def copy(self):
        return Coord(self.x, self.y)
    def to_axial(self):
        q = self.x - (self.y - (self.y&1)) / 2
        r = self.y
        return q,r
    @staticmethod
    def axial_distance(a, b):
        return (abs(a[0] - b[0]) 
            + abs(a[0] + a[1] - b[0] - b[1])
            + abs(a[1] - b[1])) / 2
    def distance(self, other):
        ac = self.to_axial()
        bc = other.to_axial()
        return int(Coord.axial_distance(ac, bc))
    def moveto(self, x, y):
        self.x = x
        self.y = y
    def move(self, direction):
        parity = self.y & 1
        self.x += direction[parity][0]
        self.y += direction[parity][1]
    def pos(self):
        return self.x,self.y
    def __str__(self):
        return f'[{self.x},{self.y}]'
    def __eq__(self, other):
        return self.pos()==other.pos()


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
    def contains(self, coord):
        if coord.x<0 or coord.y<0:
            return False
        if coord.y>=self.height:
            return False
        parity = coord.y & 1
        if parity==0:
            return coord.x<self.width
        return coord.x<self.width-1


class Unit:
    def __init__(self, figures):
        # number of figures
        self.figures = figures
        self.position = None        
    def moveto(self, x, y):
        self.position = Coord(x,y)
    def move(self, direction):
        self.position.move(direction)
    def distanceFrom(self, other):
        return self.position.distance(other.position)


class Infantry(Unit):
    def __init__(self):
        super().__init__(4)
    def kill(self):
        if self.figures>0:
            self.figures -= 1


class Dice:
    class Face(Enum):
        INFANTERY = 0
        GRENADE = 1
        TANK = 2
        FLAG = 3
        STAR = 4
        
    Str = ['🧍', '💣', '🛱', '🏴', '⭐' ]
        
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
        cls.MOVE_UP_EAST = ActionMove(Coord.Move.UP_EAST)
        cls.MOVE_UP_WEST = ActionMove(Coord.Move.UP_WEST)
        cls.MOVE_EAST = ActionMove(Coord.Move.EAST)
        cls.MOVE_WEST = ActionMove(Coord.Move.WEST)
        cls.MOVE_DOWN_EAST = ActionMove(Coord.Move.DOWN_EAST)
        cls.MOVE_DOWN_WEST = ActionMove(Coord.Move.DOWN_WEST)
        cls.All = [
                cls.NONE, cls.ATTACK,
                cls.MOVE_UP_EAST, cls.MOVE_UP_WEST, cls.MOVE_EAST, cls.MOVE_WEST, cls.MOVE_DOWN_EAST, cls.MOVE_DOWN_WEST
            ]
    def playOn(self, game):
        pass
    def availableOn(self, game):
        return True

class ActionNone(Action):
    def playOn(self, game):
        player = game.player()
        if game.phase==Phase.MOVE:
            log.debug(f'{player.name()} does not move')
        else:
            log.debug(f'{player.name()} does not atttack')
    def availableOn(self, game):
        return True
    def __str__(self):
        return 'None'

class ActionAttack(Action):
    def playOn(self, game):
        player = game.player()
        opponent = game.opponent()
        aimed = opponent.unit
        log.info(f'{player.name()} attack 1 infantry {aimed.position} with 1 infantry in {player.unit.position}')
        
        dist = player.unit.distanceFrom(aimed)
        if dist>3:
            warnings.warn('Attack with a distance grater than 3 !', RuntimeWarning)
        nbthrows = 4-dist
        dices = random.choices(Dice.Faces, k=nbthrows)
        sdices = ' '.join([Dice.Str[dice.value] for dice in dices])
        log.info(f'{player.name()} throw {sdices} ')
        
        killed = 0
        for dice in dices:
            if dice==Dice.Face.INFANTERY or dice==Dice.Face.GRENADE:
                self.kill(aimed)
                killed += 1
        log.info(f'The unit of {opponent.name()} suffers {killed} losses')
        if aimed.figures==0:
            game.player().medals += 1
    def availableOn(self, game):
        if game.phase!=Phase.ATTACK:
            return False
        player = game.player().unit
        aimed = game.opponent().unit
        dist = player.distanceFrom(aimed)
        return dist<=3
    def kill(self, aimed):
        #print('killed')
        aimed.kill()
    def __str__(self):
        return "Attack"

class ActionMove(Action):
    def __init__(self, direction):
        self.direction = direction
    def playOn(self, game):
        player = game.player()
        unit = player.unit
        oldpos = str(unit.position)
        unit.move(self.direction)
        log.info(f'{player.name()} move 1 infantery ({oldpos} to {unit.position})')
    def availableOn(self, game):
        if game.phase!=Phase.MOVE:
            return False
        other = game.opponent().unit.position
        pos = game.player().unit.position.copy()
        pos.move(self.direction)
        if other==pos:
            return False
        return game.board.contains(pos)
    def __str__(self):
        return f'Move({self.direction[2]})'

Action.Init()


class Player:
    class Side(IntEnum):
        ALLIES = 0
        AXES = 1
    def __init__(self, side):
        self.side = side
        self.unit = Infantry()
        self.medals = 0
    def name(self):
        return self.side.name


class Phase(IntEnum):
    MOVE = 0
    ATTACK = 1


class Game:
    def __init__(self):
        self.board = Board(4,5)
        self.allies = Player(Player.Side.ALLIES)
        self.allies.unit.moveto(0,0)
        self.axis = Player(Player.Side.AXES)
        self.axis.unit.moveto(3,4)
        
        self.players = [ self.allies, self.axis ]
        self.current = Player.Side.ALLIES
        
        self.phase = Phase.MOVE

    def player(self):
        return self.players[ self.current ]

    def opponent(self):
        return self.players[ (self.current+1)%2 ]

    def actions(self):
        avails = []
        for action in Action.All:
            if action.availableOn(self):
                avails.append(action)
        return avails

    def play(self, action):
        action.playOn(self)

    def next(self):
        if self.phase==Phase.MOVE:
            self.phase = Phase.ATTACK
            return
        self.switch()
        self.phase = Phase.MOVE

    def switch(self):
        """Switch player."""
        self.current = (self.current+1)%2

    def end(self):
        return self.winner() is not None

    def winner(self):
        for player in self.players:
            if player.medals>=1:
                return player.side
        return None


if __name__ =='__main__':
    from log import LoggingColor
    LoggingColor.configure(log.DEBUG)
    game = Game()
    game.player().unit.position.moveto(2,0)
    game.opponent().unit.position.moveto(0,1)
    print([str(action) for action in game.actions()])

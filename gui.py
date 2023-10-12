#!/usr/bin/python
# -*- coding: utf-8 -*-
  
from PIL import Image, ImageTk
import tkinter as tk
import threading


#zoom = 20
zoom = 40

class Hexagon:
    def __init__(self, size, fill="#a1e2a1", outline="gray"):
        self.size = size # ?
        self.fill = fill  # fill color
        self.outline = outline   # border color

    @classmethod
    def to_pixel(cls, size, x, y):
        # convert x,y to pixels
        Δx = (size**2 - (size/2)**2)**0.5
        x = Δx + 2*Δx*x + 5
        if y%2 == 1:
            x += Δx
        y = size + y*1.5*size
        return x,y
        
    def draw(self, canvas, x, y):
        size = self.size
        Δx = (size**2 - (size/2)**2)**0.5
        # convert x,y to pixels
        x,y = self.to_pixel(size, x, y)
    
        point1 = (x+Δx, y+size/2)
        point2 = (x+Δx, y-size/2)
        point3 = (x   , y-size  )
        point4 = (x-Δx, y-size/2)
        point5 = (x-Δx, y+size/2)
        point6 = (x   , y+size  )

        return canvas.create_polygon(
              point1[0], point1[1]
            , point2[0], point2[1]
            , point3[0], point3[1]
            , point4[0], point4[1]
            , point5[0], point5[1]
            , point6[0], point6[1]
            , fill=self.fill, outline=self.outline)

class HexagonGrid:
    def __init__(self, size, width, height, fill="#a1e2a1", outline="gray"):
        self.size = size
        self.width = width
        self.height = height
        self.hexagon = Hexagon(size, fill, outline)

    def dimension(self):
        Δx = (self.size**2 - (self.size/2.0)**2)**0.5
        width  = 2 * Δx * self.width + Δx
        height = 1.5*self.size*self.height + 0.5*self.size
        return (width, height)

    def draw(self, canvas):
        for y in range(self.height):
            width = self.width - y%2
            for x in range(width):
                self.hexagon.draw(canvas, x, y)

class Sprite:
    ALLY = None
    AXE = None

    offsets = [  [-17/40, -35/40]
               , [-32/40, -20/40]
               , [ -2/40, -20/40]
               , [-17/40,  -5/40] ]

    @classmethod
    def Extract(cls, units, size, rect):
        img = units.crop(rect)
        img.thumbnail((size, size))
        photo = ImageTk.PhotoImage(img)
        return Sprite(size, photo)
    
    @classmethod
    def Init(cls, size):
        units = Image.open('units.webp')
        for offset in cls.offsets:
            offset[0] *=  size
            offset[1] *=  size
        Sprite.ALLY = Sprite.Extract(units, size, (773, 36, 881, 162)) #108x126
        Sprite.AXE = Sprite.Extract(units, size, (1162, 44, 1272, 167)) #110x112

    def __init__(self, size, photo):
        self.size = size
        self.photo = photo

    def draw(self, canvas):
        return canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

    def moveto(self, canvas, id, x, y, pos=0):
        x,y = Hexagon.to_pixel(self.size, x, y)
        x += Sprite.offsets[pos][0]
        y += Sprite.offsets[pos][1]
        canvas.moveto(id, x, y)

    def hide(self, canvas, id):
        canvas.itemconfigure(id, state='hidden')


class Unit:
    def __init__(self, sprite, model):
        self.sprite = sprite
        self.size = 4
        self.units = []
        self.model = model

    def draw(self, canvas):
        for _ in range(self.size):
            unit = self.sprite.draw(canvas)
            self.units.append(unit)

    def moveto(self, canvas):
        x = self.model.position.x
        y = self.model.position.y
        for pos,unit in enumerate(self.units):
            self.sprite.moveto(canvas, unit, x, y, pos)

    def show(self, canvas):
        size = self.model.figures
        for pos,unit in enumerate(self.units):
            if pos>=size:
                self.sprite.hide(canvas, unit)

    def update(self, canvas):
        self.moveto(canvas)
        self.show(canvas)


class App:
    def __init__(self, game):
        self.game = game

        root = tk.Tk()
        self.root = root;
        root.protocol("WM_DELETE_WINDOW", self.delete_window)

        root.title("Memoir 44")

        width = game.board.width
        height = game.board.height
        
        self.grid = HexagonGrid(zoom, width, height)

        dim = self.grid.dimension()

        self.canvas = tk.Canvas(self.root, width=dim[0], height=dim[1])
        self.canvas.pack()

        #self.can.bind("<Button-1>", self.click)

        Sprite.Init(zoom)
        self.allies = Unit(Sprite.ALLY, game.allies.unit)
        self.axis = Unit(Sprite.AXE, game.axis.unit)
        
        self.draw(self.canvas)
        
        self.update()

    def draw(self, canvas):
        self.grid.draw(canvas)
        self.allies.draw(canvas)
        self.axis.draw(canvas)

    def update(self):
        self.allies.update(self.canvas)
        self.axis.update(self.canvas)

    def delete_window(self):
        self.root.quit()

    def mainloop(self):
        self.root.mainloop()

    def click(self, evt):
        """
        hexagon detection on mouse click
        """
        #print('click', evt)
        #x , y = evt.x, evt.y
        #for i in self.hexagons:
            #i.selected = False
            #i.isNeighbour = False
            #self.can.itemconfigure(i.tags, fill=i.color)
        #clicked = self.can.find_closest(x, y)[0] # find closest
        #self.hexagons[int(clicked)-1].selected = True
        #for i in self.hexagons: # re-configure selected only
            #if i.selected:
                #self.can.itemconfigure(i.tags, fill="#53ca53")
            #if i.isNeighbour:
                #self.can.itemconfigure(i.tags, fill="#76d576")


class ThreadApp(threading.Thread):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.app = None
        self.app_ready = threading.Condition()
        self.start()

    def run(self):
        self.app = App(self.game)
        with self.app_ready:
            self.app_ready.notify()
        self.app.mainloop()
    
    def update(self):
        if self.app is None:
            with self.app_ready:
                self.app_ready.wait()
        self.app.update()


if __name__ =='__main__':
    import time
    
    from arena import Arena, Callback
    from players import *
    
    class Gui(Callback):
        def __init__(self):
            pass

        def start(self, game):
            self.thread = ThreadApp(game)

        def end(self, game, winner_num, winner_player):
            print('end turn')
            self.thread.update()
            self.thread.join()

        def turn(self, game):
            self.thread.update()
            time.sleep(1)

    gui = Gui()

    arena = Arena(gui)
    arena.play([PlayerAttack(), PlayerRandom()], 1)

import csv
import pickle
from os.path import exists
from linkedlist import CLinkedList

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Quad
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.behaviors import DragBehavior
#   --get detection (basic contact) to work with floor
#   --make filter a quad representing ground surface
#   find a way to define "ground" quad from code
#   separate def for wall and floor deco
#   set up walldeco detection
#   set save to disabled if a filter is red
#   fix up data structure
#   pets, self as little animated things
#   crafting mechanism!


def point_inside_polygon(x, y, poly):
    '''Taken from http://www.ariel.com.au/a/python-point-int-poly.html
    '''
    n = len(poly)
    inside = False
    p1x = poly[0]
    p1y = poly[1]
    for i in range(0, n + 2, 2):
        p2x = poly[i % n]
        p2y = poly[(i + 1) % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside



studio_state = {}

class Furniture(DragBehavior,Widget):
    pictures = ObjectProperty(None)
    img = ObjectProperty(None)
    filterColor = ListProperty([0, 0,0,0])
    area = ObjectProperty(None)
    ground = ListProperty([0, 0, 0, 0, 0, 0, 0, 0])
    def __init__(self, toy, pos, **kwargs):
        super().__init__(**kwargs)

        self.id = toy[0]
        self.size = (int(toy[1]),int(toy[2]))
        self.pos = pos
        self.drag_rectangle = (self.x, self.y, int(toy[1]),int(toy[2]))

        img = self.canvas.children[1]
        img.source = "img/"+toy[3]
        img.size = (int(toy[1]),int(toy[2]))
        self.pictures = CLinkedList()
        for i in range(3,7):
            if toy[i] != "":
                self.pictures.append(toy[i])

        self.area = self.canvas.get_group('filter')[1]
        #print(self.area.points)

    def on_touch_down(self, touch):
        if touch.button == 'right':
            if self.collide_point(*touch.pos):
                self.canvas.children[1].source = "img/"+self.pictures.next().val
                return True
        if touch.button == 'left':
            #bring to front
            parent = self.parent
            parent.remove_widget(self)
            parent.add_widget(self)

        return super(Furniture, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.parent.floor.contains_widget(self):#self.parent.floor.collide_point(touch.x,touch.y):
            self.filterColor = 1,0,0,0.5
        else:
            self.filterColor = 0,0,1,0.5
        return super(Furniture,self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            studio_state[self.id] = [self.x, self.y]
        return super(Furniture, self).on_touch_up(touch)

class Floor(Widget):
    p1 = ListProperty([0, 0])
    p2 = ListProperty([0, 0])
    p3 = ListProperty([0, 0])
    p4 = ListProperty([0, 0])
    area = ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.center_x = Window.width//2
        self.center_y = Window.height//2
    def setup(self):
        self.area = self.canvas.get_group('a')[0]

    def on_touch_down(self, touch):
        return super(Floor, self).on_touch_down(touch)

    def contains_widget(self, item):
        inside = True

        for i in range(len(item.area.points) //2):
            ptX = item.area.points[i*2]
            ptY = item.area.points[i*2+1]
            if not(self.collide_point(ptX,ptY)):
                inside = False
        return inside

    def collide_point(self, x, y):
        x, y = self.to_local(x, y)
        return point_inside_polygon(x, y, self.area.points)


class Wall(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.center_x = Window.width//2
        self.center_y = Window.height//2
    pass

class Studio(Widget):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        with open("furniture.csv") as file_name:
            read_csv = csv.reader(file_name)
            toys = list(read_csv)
        #Floor()
        global studio_state
        if exists("studio_state.pkl"):
            with open("studio_state.pkl", "rb") as f:
                studio_state = pickle.load(f)
        else:
            studio_state = {}
        i=1
        for t in toys:
            toypos = studio_state[t[0]] if t[0] in studio_state else [0,0]
            f = Furniture(t, toypos)#, positions[t[0]])
            self.add_widget(f)
            i+=1

        btn = Button(text="Save", pos = (100,0))
        btn.bind(on_press=self.doThings)
        self.add_widget(btn)
        self.floor.setup()
        #self.wall.setup()
    def doThings(self, evt):
        # save state to file
        print(studio_state)
        with open("studio_state.pkl", "wb") as f:
            pickle.dump(studio_state, f)

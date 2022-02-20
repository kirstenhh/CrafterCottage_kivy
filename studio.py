import csv
import pickle
from os.path import exists
from linkedlist import CLinkedList

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Quad
from kivy.properties import ObjectProperty, ListProperty, DictProperty
from kivy.uix.button import Button
from kivy.uix.behaviors import DragBehavior
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

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
def contains_widget(container, item):
    inside = True
    for i in range(len(item.area.points) //2):
        ptX = item.area.points[i*2]
        ptY = item.area.points[i*2+1]
        if not(container.collide_point(ptX,ptY)):
            inside = False
    return inside



class Furniture(Widget):
    pictures = ObjectProperty(None)
    img = ObjectProperty(None)
    ground = ListProperty([0,0,0,0,0,0,0,0])
    def __init__(self, furniture, **kwargs):
        super().__init__(**kwargs)
        self.id=furniture[0]
        self.size = (int(furniture[1]),int(furniture[2]))
        img = self.canvas.children[1]
        img.source = "img/"+furniture[3]
        img.size = (self.width, self.height)

class PlacedFurniture(DragBehavior, Furniture):
    filterColor = ListProperty([0,0, 0,0])
    area = ObjectProperty(None)
    #furniture: id, width, height, image1, image2, [image3], [image4], type
    def __init__(self, furniture, pos=[0,0], **kwargs):
        super().__init__(furniture=furniture, **kwargs)
        if(pos != [0,0]):
            self.pos = pos

        self.drag_timeout = 100000
        drag_distance = 0
        self.drag_rectangle = (self.x, self.y, self.width, self.height)

        self.pictures = CLinkedList()
        for i in range(3,7):
            if furniture[i] != "":
                self.pictures.append(furniture[i])
        self.area = self.canvas.get_group('filter')[1]

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if touch.button == 'right':
                    self.canvas.children[1].source = "img/"+self.pictures.next().val
                    return True
        return super().on_touch_down(touch)

class StoredFurniture(Furniture):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            print(self.id)


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
    furniture = ListProperty([])
    placements = {}
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        with open("furniture.csv") as file:
            read_csv = csv.reader(file)
            existingfurniture ={}
            for row in list(read_csv):
                existingfurniture[row[0]] = row

        if exists("placed_state.pkl"):
            with open("placed_state.pkl", "rb") as file:
                self.placements = pickle.load(file)
        else:
            self.placements = {}

        #TODO: swap existingfurniture for "owned" object
        for fid in existingfurniture:
            if fid in self.placements:
                self.addFurniture(existingfurniture[fid], self.placements[fid])
            else:
                newf = StoredFurniture(existingfurniture[fid])
                self.owned.inventory.add_widget(newf)

        #Testing only! remember to cut when store/inventory work
        # for ff in existingfurniture:
        #     newf=Furniture(existingfurniture[ff])
        #     self.furniture.append(newf)
        #     self.add_widget(newf)

        self.floor.setup()
        #self.wall.setup()
    def addFurniture(self, furniture, pos=[0,0]):
        if pos==[0,0]:
            pos= [self.center_x, self.center_y]
        newf = PlacedFurniture(furniture, pos=pos)
        self.furniture.append(newf)
        self.add_widget(newf)
    def savePos(self):
        # save state to file
        for ff in self.furniture:
            if ff.pos !=[0,0]:
                self.placements[ff.id] = [ff.x, ff.y]
        with open("placed_state.pkl", "wb") as f:
            pickle.dump(self.placements, f)
        print("Saved")
    #on touch down:
        # if touch on inventoryFurniture: new PlacedFurniture(a)
    def on_touch_move(self, touch):
        for furniture in self.furniture:
            if contains_widget(self.floor, furniture):
                furniture.filterColor = 1,0,0,0.5
            else:
                furniture.filterColor = 0,0,1,0.5
        return super().on_touch_move(touch)

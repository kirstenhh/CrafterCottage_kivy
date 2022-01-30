import csv
import pickle
from os.path import exists
from linkedlist import CLinkedList

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Quad
from kivy.properties import ObjectProperty, ListProperty, DictProperty
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
def contains_widget(container, item):
    inside = True
    for i in range(len(item.area.points) //2):
        ptX = item.area.points[i*2]
        ptY = item.area.points[i*2+1]
        if not(container.collide_point(ptX,ptY)):
            inside = False
    return inside



class Furniture(DragBehavior,Widget):
    pictures = ObjectProperty(None)
    img = ObjectProperty(None)
    filterColor = ListProperty([0, 0,0,0])
    area = ObjectProperty(None)
    ground = ListProperty([0, 0, 0, 0, 0, 0, 0, 0])
    #furniture: id, width, height, image1, image2, [image3], [image4], type
    def __init__(self, furniture, pos=[0,0], **kwargs):
        super().__init__(**kwargs)

        self.pos = pos
        self.id=furniture[0]
        self.size = (int(furniture[1]),int(furniture[2]))
        self.drag_rectangle = (self.x, self.y, self.width, self.height)

        img = self.canvas.children[1]
        img.source = "img/"+furniture[3]
        img.size = (self.width, self.height)
        self.pictures = CLinkedList()
        for i in range(3,7):
            if furniture[i] != "":
                self.pictures.append(furniture[i])

        self.area = self.canvas.get_group('filter')[1]

    def on_touch_down(self, touch):
        if touch.button == 'right':
            if self.collide_point(*touch.pos):
                self.canvas.children[1].source = "img/"+self.pictures.next().val
                return True
        if touch.button == 'left':
            parent = self.parent
            # parent.remove_widget(self)
            # parent.add_widget(self)
        return super().on_touch_down(touch)


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
        print(self.placements)
        for fpos in self.placements:
            print(fpos)
            info = existingfurniture
            newf = Furniture(existingfurniture[fpos], pos=self.placements[fpos])
            #studio_state[self.id] = [self.x, self.y]
            self.furniture.append(newf)
            self.add_widget(newf)

        #Testing only! remember to cut when store/inventory work
        # for ff in existingfurniture:
        #     newf=Furniture(ff)
        #     self.furniture.append(newf)
        #     self.add_widget(newf)

        # for t in toys:
        #     if t[0] in studio_state:
        #         f = Furniture(t, studio_state[t[0]])#, positions[t[0]])
        #         #self.placed_furniture.add_widget(placed_furniture)
        #         self.add_widget(f)
        #         self.furniture.add(f)
        #
        #     else:
        #         f = Furniture(t, [0,0])
        #         self.furniture.add(f)
        #
        #         #self.owned.add_widget(f)
        #         pass
        #     i+=1

        btn = Button(text="Save", pos = (100,0))
        btn.bind(on_press=self.savePos)
        self.add_widget(btn)
        self.floor.setup()
        #self.wall.setup()
    def savePos(self, evt):
        # save state to file
        for ff in self.furniture:
            if ff.pos !=[0,0]:
                self.placements[ff.id] = [ff.x, ff.y]

        with open("placed_state.pkl", "wb") as f:
            pickle.dump(self.placements, f)


    def on_touch_move(self, touch):

        for furniture in self.furniture:
            if contains_widget(self.floor, furniture):
                furniture.filterColor = 1,0,0,0.5
            else:
                furniture.filterColor = 0,0,1,0.5
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):

        for furniture in self.furniture:
            if furniture.collide_point(*touch.pos):
                #print(furniture.x)
                pass

        return super().on_touch_up(touch)

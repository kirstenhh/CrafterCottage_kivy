from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.app import App
from kivy.uix.behaviors import DragBehavior
from kivy.lang import Builder

# You could also put the following in your kv file...
kv = '''
<DragWidget>:
    # Define the properties for the DragLabel
    drag_rectangle: self.x, self.y, self.width, self.height
    drag_timeout: 10000000
    drag_distance: 0
    size: 50,50
    canvas:
        Color:
            rgb: (1,0,1)
        Rectangle:
            pos: self.pos
            size: self.size
<CollideWidget>:
    canvas:
        Color:
            rgb: (0,1,1)
        Quad:
            points: (self.x,self.y+100,  self.x,self.y,  self.x+200,self.y,  self.x,self.y+200)


FloatLayout:
    RootWidget:
        triangle: collide_widget
        square: drag_widget
        CollideWidget:
            id: collide_widget
            pos: (300,300)
        DragWidget:
            id: drag_widget
            size_hint: 0.25, 0.2
            pos: (0,0)

'''

class CollideWidget(Widget):
    pass

class DragWidget(DragBehavior, Widget):
    pass

class RootWidget(Widget):
    def on_touch_move(self, touch):
        if self.triangle.collide_widget(self.square):
            print("zip")
        super().on_touch_move(touch)

class TestApp(App):
    def build(self):
        return Builder.load_string(kv)

TestApp().run()

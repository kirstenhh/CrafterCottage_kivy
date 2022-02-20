import math
from kivy.animation import Animation
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Quad, Ellipse
from kivy.properties import (
    NumericProperty,ListProperty,
    ReferenceListProperty,ObjectProperty
)
from kivy.vector import Vector
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from random import randint
from kivy.core.window import Window
from kivy.uix.popup import Popup

#To do:
#   --Health bar
#   --Levels
#   --Randomise enemy movement
#   clear bullets on new level
#   --Enemy types
#   types 1-7?
#   obstacles?
#   --Scoring system+display
#   save score (for "money"), save game level
#   --design: make player movable,
#   reorganize
#   --health depending on bottom target rather than player
#   shake/animation reaction on hit
#   player has the ability to use a bomb?
#   add object drop for enemies: vanish in ~5 seconds, and 5 seconds available after last enemy dies?
#   -- continue/quit,
#   default to continue
#   -- move health to "door" instead of player?
#   bounce enemies off player
#   https://github.com/kivy-garden/garden.joystick for mobile (wasd for desktop)
#   Make movement account for framerate


######### GAME ELEMENTS ########################

#speed: ~ 1-10
def getVector(origin, dest, speed):
    length = math.sqrt(math.pow((dest.x-origin.x),2)+math.pow((dest.y-origin.y),2))
    dx = speed*(dest.x - origin.x)/length
    dy = speed*(dest.y -origin.y)/length
    return Vector(dx,dy)

def levelEnd():
    content = LevelEnd()
    pop = Popup(title="Done", content=content, size_hint=(None,None), size=(200,200), auto_dismiss=False)
    content.btn_gohome.bind(on_press=pop.dismiss)
    content.btn_nextlevel.bind(on_press=pop.dismiss)
    pop.open()

def dead():
    pass

def randenemy(level):
    highest = (1+level//10) if level<70 else 7
    type = randint(1, 2)
    if type==1:
        return EnemyBasic()
    else:
        return EnemyBig()

class Bullet(Widget):
    velocity_x = NumericProperty(None)#randint(0,4))
    velocity_y = NumericProperty(None)#randint(0,4))
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    def move(self):
        self.pos =  Vector(*self.velocity) + self.pos

# Superclass for enemies
#   other types: will fire and drop different things.
class Enemy(Widget):
    velocity_x = NumericProperty(None)
    velocity_y = NumericProperty(None)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    life = NumericProperty(0)  # changes for different enemy types
    #life, size, velocity
    # changes of vector and application of current vector
    def move(self):
        pass
    # if the enemy type has an action, i.e. fire projectiles
    def randact(self):
        pass
    #   make possible drops: money, plus supplies
    #   % chance of money drop, % chance of supply drop; supply type is ~ random
    def randdrop(self):
        pass

class EnemyBasic(Enemy):
    img = ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.life = 40
        self.size = (20,20)
        with self.canvas:
            Color(0.2, 0.8,0.8)
            self.img = Ellipse(pos = self.pos, size = self.size)
    def move(self):
        self.pos =  Vector(*self.velocity) + self.pos
        self.img.pos = self.pos
        if self.x<0 or self.x>Window.width:
            self.velocity_x*=-1
        if self.y<0 or self.y>Window.height:
            self.velocity_y*=-1
    def on_hit(self, hit):
        #future: include type of hit for damage
        self.randdrop()
        self.life-=1
    def randdrop(self):
        if randint(0,100)<10:
            print("drop")
            #dropcash(5) or a random quantity (spawn cash widget)

class EnemyBig(Enemy):
    img = ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.life = 40
        self.size = (60,30)
        with self.canvas:
            Color(0.8,0.8,0.2)
            self.img = Ellipse(pos = self.pos, size = self.size)
    def move(self):
        self.pos =  Vector(*self.velocity) + self.pos
        self.img.pos = self.pos
        if self.x<0 or self.x>Window.width or randint(0,20)<=1 :
            self.velocity_x*=-1
        if self.y<0 or self.y>Window.height:
            self.velocity_y*=-1
    def on_hit(self, hit):
        #future: include type of hit for damage
        self.randdrop()
        self.life-=1
    def randdrop(self):
        if randint(0,100)<10:
            print("drop")
            #dropcash(5) or a random quantity (spawn cash widget)


#"door"; takes health damage
class Target(Widget):
    health = NumericProperty(100)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        health = 100 #replace with file data from the studio


# player; takes no health damage, bullets start here, moves around
class Player(Widget):
    score = NumericProperty(0)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down = self._on_key_down)
        self._keyboard.bind(on_key_up = self._on_key_up)
        self._keysDown = set()

    def _on_keyboard_closed(self):
        self._keyboard.unbind(on_key_down = self._on_key_down)
        self._keyboard.unbind(on_key_up = self._on_key_up)
        self._keyboard = None
    def _on_key_down(self,keyboard,keycode,text,modifiers):
        self._keysDown.add(text)
    def _on_key_up(self,keyboard,keycode):
        if keycode[1] in self._keysDown:
            self._keysDown.remove(keycode[1])
    def move(self):
        v=6
        for c in self._keysDown:
            if c=='w':
                self.y+=v
            if c=='a':
                self.x-=v
            if c=='s':
                self.y-=v
            if c=='d':
                self.x+=v

###### Page elements ##################
class LevelEnd(FloatLayout):
    pass



class BattleGame(Widget):
    level = NumericProperty(1)
    player = ObjectProperty(None)
    target = ObjectProperty(None)
    enemies = ListProperty([])
    bullets = ListProperty([])


    def start(self):
        self.clock = Clock.schedule_interval(self.update, 1/60)
        enemyCount = 5*self.level#change to randomize/endless
        for i in range(0,enemyCount):
            spawn = randenemy(self.level)
            spawn.pos = (randint(10, self.width - 10),self.height -20)
            spawn.velocity = getVector(spawn, self.target, randint(1,3))
            self.enemies.append(spawn)
            self.add_widget(spawn)

    def on_touch_down(self, touch):
        #create a bullet (change to "attack" when there are multiple types; get data from files?)
        speed = 5
        shot = Bullet()
        shot.pos = self.player.pos
        shot.size = 10,10
        shot.velocity = getVector(self.player, touch, speed)
        self.bullets.append(shot)
        self.add_widget(shot)
        super().on_touch_down(touch)
    def update(self,dt):
        #player
        if self.target.health <=0:
            self.add_widget(Label(text="Dead"))
        self.player.move()
        remove = set()
        #enemies
        for en in self.enemies:
            if en.collide_widget(self.target):
                self.target.health -=1
            en.move()

            for b in self.bullets:
                if en.collide_widget(b):
                    en.life-=10
                    remove.add(b)
            if en.life <=0:
                self.enemies.remove(en)
                self.player.score+=1    #increment for different enemy types
                self.remove_widget(en)

        if len(self.enemies) ==0:
            levelEnd()
            self.level +=1
            self.clock.cancel()
            for r in remove:
                self.bullets.remove(r)
                self.remove_widget(r)
        #removeRange?
        else:
            for r in remove:
                self.bullets.remove(r)
                self.remove_widget(r)
            #bullets
            for b in self.bullets:
                b.move()
                if b.x<0 or b.x>self.width or b.y<0 or b.y>self.height:
                    self.bullets.remove(b)
                    self.remove_widget(b)

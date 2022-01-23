
#To Do:
#   ---save positions to file for studio (save user info in general)
#   fix framerate for game movement
#   change game to match idea - door for health
#   work out what I want to do with resizing
#   hash out a basic UI
#   implement levels + coins for battle
#   implement store??
#   Music?
#   find art and/or an artist
#   colour choices?

#:kivy 2.0.0
from battle import BattleGame
from studio import Studio

from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget

Builder.load_file('battle.kv')
Builder.load_file('studio.kv')

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('graphics', 'width', '1920')
Config.set('graphics', 'height', '1080')


class HearthView(Screen):
    studio = ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        studio = Studio()
        studio.size = Window.size
        self.add_widget(studio)
        self.studio = studio


class PlayView(Screen):
    game = ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        game = BattleGame()
        game.size = Window.size
        self.add_widget(game)
        self.game = game
    def on_enter(self):
        super().on_enter()
        self.game.start()

class GameManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = Window.size
    def next_level_game(self):
        self.get_screen("battle").game.start()
    pass

class CrafterApp(App):
    pass

if __name__ == '__main__':
    CrafterApp().run()

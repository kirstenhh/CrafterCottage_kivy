from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
#:kivy 2.0.0


class CodedPhrase(Widget):
    def get_encoded():
        with open("phrases") as phrases_file:
            phrase = phrases_file.readline()
            encode = encode(phrase)
    def encode(phrase):
        


class DecoderGame(Widget):
    pass

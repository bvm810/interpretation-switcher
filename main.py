# Main python file for creating the GUI using the kv file switcher.kv

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics.svg import Svg
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image


Builder.load_file("./switcher.kv")

class BackgroundWidget(FloatLayout):
    pass

class SongboxWidget(BoxLayout):
    pass

class SheetboxWidget(BoxLayout):
    pass


#BACKEND MAGIC
root = BackgroundWidget()
songbox = SongboxWidget(size_hint= (0.3, 0.9),pos_hint={"x":0.0, "y": 0.1})
sheetbox = SheetboxWidget(size_hint= (0.7, 0.9),pos_hint={"x":0.3, "y": 0.1})

root.add_widget(songbox)
root.add_widget(sheetbox)

class MainApp(App):

    def build(self):
        return root

if __name__ == '__main__':
    MainApp().run()

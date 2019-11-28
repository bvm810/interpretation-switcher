# Main python file for creating the GUI using the kv file switcher.kv

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label


root = Builder.load_file("./switcher.kv") # Loads GUI background and basic displays

# Creates a box layout on the left-hand side to house the song progress bars
songbox = BoxLayout(
    orientation = "vertical",
    size_hint=(0.3, 0.8),
    pos_hint={'x': 0.0, 'y': 0.2})

# Creates a box on the right hand side to house the music sheet image
sheetbox = BoxLayout(
    orientation = "vertical",
    size_hint=(0.7, 0.8),
    pos_hint={'x': 0.3, 'y': 0.2})

root.add_widget(songbox)

class MainApp(App):

    def build(self):
        return root

if __name__ == '__main__':
    MainApp().run()

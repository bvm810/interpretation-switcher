# Main python file for creating the GUI using the kv file switcher.kv

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty

class MainWindow(Screen):
    filename = ObjectProperty(None)

class WindowManager(ScreenManager):
    pass

kv = Builder.load_file("switcher.kv")
sm = WindowManager()

screens = [MainWindow(name="main")]

for screen in screens:
    sm.add_widget(screen)

sm.current = "main"

class MyMainApp(App):
    def build(self):
        return sm

if __name__ == "__main__":
    MyMainApp().run()

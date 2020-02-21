# Main python file for creating the GUI using the kv file main.kv

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from switcher.switcher import SwitcherLayout
from kivy.core.window import Window


Builder.load_file("./main.kv")

class Background(FloatLayout):
    pass

class MainApp(App):

    def build(self):
        Window.size = (800, 100)
        Window.bind(on_request_close=self.on_request_close)
        root = Background()
        filelist = ['Chopin Prelude Op. 28 No. 7 MIDI.wav', 'Chopin Prelude Op. 28 No. 7 N. Freire.wav', 'Chopin Prelude Op. 28 No. 7 M. Pollini.wav']
        self.songbox = SwitcherLayout(filelist, size_hint= (0.3, 0.8),pos_hint={"x":0.0, "y": 0.2})

        root.add_widget(self.songbox)
        return root

    def on_request_close(self, *args):
        self.songbox.switcher.close()
        Window.close()
        return True

if __name__ == '__main__':
    MainApp().run()

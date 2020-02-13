import pyaudio
import wave
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.clock import Clock

class PlayerWidget(Widget):

    def __init__(self, filename, **kwargs):
        super().__init__(**kwargs)
        self.is_playing = False
        self.currentSample = 0
        self.chunk = 1024
        self.file = wave.open(filename, 'rb')

        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(format=self.p.get_format_from_width(self.file.getsampwidth()),
                channels=self.file.getnchannels(),
                rate=self.file.getframerate(),
                output=True)

        Clock.schedule_interval(self.callback, (self.chunk/self.file.getframerate())/2)

        play_button = Button(text = 'play', pos=(0,0), size=(100,100))
        pause_button = Button(text = 'pause', pos=(0,150), size = (100,100))
        getpos_button = Button(text = 'get_time', pos=(150,0), size = (100,100))
        rewind_button = Button(text = 'rewind', pos=(150,150), size = (100,100))

        self.add_widget(play_button)
        self.add_widget(pause_button)
        self.add_widget(getpos_button)
        self.add_widget(rewind_button)

        play_button.on_press = self.play
        pause_button.on_press = self.pause

    def play(self):
        self.is_playing = True

    def pause(self):
        self.is_playing = False

    def callback(self, dt):
        if self.is_playing == True:
            data = self.file.readframes(self.chunk)
            if len(data) <= 0:
                self.stream.stop_stream()
                self.stream.close()
                self.p.terminate()
                return False
            self.stream.write(data)


class TestApp(App):
    def build(self):
        player = PlayerWidget('Chopin Prelude Op. 28 No. 7 N. Freire.wav')
        return player

if __name__ == '__main__':
    TestApp().run()

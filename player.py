import pyaudio
import wave
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.clock import Clock

class PlayerWidget(Widget):
    """
        Class created for being able to play a song and get the necessary information for the interpretation switcher
    """

    def __init__(self, filename, **kwargs):
        super().__init__(**kwargs) # Necessary since it inherits from Widget
        self.is_playing = False # Flag to see if it is playing
        self.currentSample = 0 # Attribute to save current sample of audio
        self.chunk = 1024 # Number of samples to read at each callback
        self.file = wave.open(filename, 'rb') # .wav file

        self.p = pyaudio.PyAudio() # PyAudio player object

        # PyAudio Stream object
        self.stream = self.p.open(format=self.p.get_format_from_width(self.file.getsampwidth()),
                channels=self.file.getnchannels(),
                rate=self.file.getframerate(),
                output=True)

        # Use of Kivy clock to schedule callbacks
        Clock.schedule_interval(self.callback, (self.chunk/self.file.getframerate())/2)

        # Widget buttons
        play_button = Button(text = 'play', pos=(0,0), size=(100,100))
        pause_button = Button(text = 'pause', pos=(0,150), size = (100,100))
        getpos_button = Button(text = 'get_time', pos=(150,0), size = (100,100))
        rewind_button = Button(text = 'rewind', pos=(150,150), size = (100,100))

        self.add_widget(play_button)
        self.add_widget(pause_button)
        self.add_widget(getpos_button)
        self.add_widget(rewind_button)

        aux_fun = lambda : self.set_pos(1349632)
        play_button.on_press = self.play
        pause_button.on_press = self.pause
        getpos_button.on_press = self.get_sample
        rewind_button.on_press = aux_fun

    # Method for playing
    def play(self):
        self.is_playing = True

    # Method for pausing
    def pause(self):
        self.is_playing = False

    # Method for getting current audio sample
    def get_sample(self):
        self.currentSample = self.file.tell()
        print(self.currentSample)

    #Method for going to a specific audio sample
    def set_pos(self, pos):
        self.file.setpos(pos)
        self.currentSample = pos

    # Method for reading self.chunk samples at a time. It is called regularly by the kivy digital clock
    def callback(self, dt):
        if self.is_playing == True:
            data = self.file.readframes(self.chunk)
            if len(data) <= 0:
                self.file.rewind()
                self.is_playing = False
            self.stream.write(data)


class TestApp(App):
    def build(self):
        player = PlayerWidget('Chopin Prelude Op. 28 No. 7 N. Freire.wav')
        return player

if __name__ == '__main__':
    TestApp().run()

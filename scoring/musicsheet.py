# Create songbox widget to be added to main.
# To do: first version of musical drawing

from midread import Note
from midread import get_notes
from midread import get_active_notes
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.clock import Clock

class ScoreWidget(Widget):
    """
    Class responsible for parsing midi, writing song score and highliting active notes
    """
    # Initializing
    def __init__(self, midi, switcher, **kwargs):
        super().__init__(**kwargs)
        self.notes = get_notes(midi) # Midi note parsing
        self.current_notes = [] # List containing active notes. To be updated regularly
        self.switcher = switcher # Corresponding switcher

        # Use of Kivy clock to schedule update of current notes
        sample_interval = self.switcher.players[0].chunk # In case of parameter customization, think about changing
        fs = self.switcher.players[0].file.getframerate() # these two variables to attributes to hop_size and fs
        self.clock = Clock.schedule_interval(self.callback, sample_interval/fs)

    def callback(self, dt): # method for updating current_notes
        origin = self.switcher.players.index(self.switcher.currentPlayer) # Check in which audio I am
        origin_frame = self.switcher.currentPlayer.get_frame()
        if origin == 0: # If in MIDI corresponding .wav file, get current frame
            frame = origin_frame
        else: # Else get corresponding frame
            frame = self.switcher.get_corresponding_frame(origin, 0, origin_frame, method = 'avg')
        self.current_notes = get_active_notes(self.notes, frame)

    def close(self):
        Clock.unschedule(self.clock)

class ScoreLayout(FloatLayout):
    def __init__(self, midi, switcher, **kwargs):
        super().__init__(**kwargs)
        self.score = ScoreWidget(midi, switcher)
        print_notes = Button(text = 'Print Active Notes !', text_size = self.size, size_hint= (1, 1),pos_hint={"x":0.0, "y": 0.0})
        print_notes.on_press = self.print_current_notes
        self.add_widget(print_notes)

    def print_current_notes(self):
        for note in self.score.current_notes:
            print('Pitch: {}, Start Time: {:.2f}, End Time: {:.2f}, Duration: {}'.format(note.pitch, note.start, note.end, note.duration))

    def close(self):
        self.score.close()

# Create songbox widget to be added to main.
# To do: first version of musical drawing

# Step 1: Until 07/04 -> Draw stave


from scoring.midread import Note
from scoring.midread import get_notes
from scoring.midread import get_active_notes
from kivy.uix.boxlayout import BoxLayout
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

class MeasureWidget(Widget):
    """
    Widget for drawing a measure. Largely based on the work in https://github.com/Syncrossus/Perfect-Melody/blob/master/gui/scorewidget.py
    """

    # Constants
    start_line_treble = 30
    start_line_bass = 130
    line_separation = 10

class StaveLayout(BoxLayout):
    """
    Widget for drawing the stave. Also based on https://github.com/Syncrossus/Perfect-Melody/blob/master/gui/scorewidget.py
    Is merely a constructor for the layout present in the kv file
    """
    pass

class ScoreLayout(FloatLayout):
    def __init__(self, midi, switcher, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.score = ScoreWidget(midi, switcher)
        stave = StaveLayout(size_hint= (0.75, 1),pos_hint={"x":0.0, "y": 0.0})
        print_notes = Button(text = 'Print Active Notes !', text_size = self.size, size_hint= (0.25, 1),pos_hint={"x":0.75, "y": 0.0})
        print_notes.on_press = self.print_current_notes
        self.add_widget(stave)
        self.add_widget(print_notes)

    def print_current_notes(self):
        for note in self.score.current_notes:
            print('Pitch: {}, Start Time: {:.2f}, End Time: {:.2f}, Duration: {}'.format(note.pitch, note.start, note.end, note.duration))

    def close(self):
        self.score.close()

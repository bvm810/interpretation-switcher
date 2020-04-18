# Create songbox widget to be added to main.
# To do: first version of musical drawing

# Step 1: Until 30/04 -> Working first version
# Current stage -> Toggling notes method not working. Try scrolling line
# TO DO:
# 1) Auto-update stave
# 2) Adapt position to get x-coord for notes
# 3) Create method for drawing line
# 4) Auto-update line


from scoring.midread import NoteWidget
from scoring.midread import get_notes
from scoring.midread import get_active_notes
from scoring.midread import midi2note
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Line
from kivy.uix.widget import Widget
from kivy.clock import Clock

class ScoreWidget(Widget):
    """
    Class responsible for parsing midi and detecting active notes
    """
    # Initializing
    def __init__(self, midi, switcher, **kwargs):
        super().__init__(**kwargs)
        self.notes = get_notes(midi) # Midi note parsing
        self.current_notes = [] # List containing active notes. To be updated regularly
        self.previous_notes = []
        self.switcher = switcher # Corresponding switcher

        # Use of Kivy clock to schedule update of current notes
        sample_interval = self.switcher.players[0].chunk # In case of parameter customization, think about changing
        fs = self.switcher.players[0].file.getframerate() # these two variables to attributes to hop_size and fs
        self.clock = Clock.schedule_interval(self.callback, sample_interval/fs)

    # Method for highlighting notes currently being played
    def callback(self, dt):
        self.update_current_notes() # Update current notes
        self.toggle_notes() # Turn all notes on

    # Method for highlighting active notes
    def toggle_notes(self):
        for previous_note in self.previous_notes:
            if previous_note not in self.current_notes:
                previous_note.toggle()
        for current_note in self.current_notes:
            if current_note not in self.previous_notes:
                current_note.toggle()

    # Method for updating active notes
    def update_current_notes(self):
        origin = self.switcher.players.index(self.switcher.currentPlayer) # Check in which audio I am
        origin_frame = self.switcher.currentPlayer.get_frame()
        if origin == 0: # If in MIDI corresponding .wav file, get current frame
            frame = origin_frame
        else: # Else get corresponding frame
            frame = self.switcher.get_corresponding_frame(origin, 0, origin_frame, method = 'avg')
        self.previous_notes = self.current_notes
        self.current_notes = get_active_notes(self.notes, frame)

    def close(self):
        Clock.unschedule(self.clock)

class MeasureWidget(FloatLayout):
    """
    Widget for drawing a measure. Largely based on the work in https://github.com/Syncrossus/Perfect-Melody/blob/master/gui/scorewidget.py
    Should contain all required methods for drawing a measure
    """

    # Constants
    start_line_treble = 150
    start_line_bass = 270
    line_separation = 15
    note_letters = 'CDEFGAB'
    bass_octaves = [0, 1, 2, 3]
    treble_octaves = [4, 5, 6, 7, 8]

    def display(self, notes):

        # Constants that depend on self
        self.first_line_treble = self.top - self.start_line_treble
        self.third_line_treble = self.first_line_treble - self.line_separation * 2
        self.fifth_line_treble = self.third_line_treble - self.line_separation * 2
        # Lowest note of treble key is central C
        self.lower_note_treble = self.fifth_line_treble - self.line_separation

        self.first_line_bass = self.top - self.start_line_bass
        self.third_line_bass = self.first_line_bass - self.line_separation * 2
        self.fifth_line_bass = self.third_line_bass - self.line_separation * 2
        # Lowest line of bass key minus one octave and one note minus 5 notes -> A0
        self.lower_note_bass = self.fifth_line_bass - (self.line_separation * 4 + self.line_separation * 5)

        self.current_x = self.x + self.width * 0.04 # Position for first note
        self.current_onset = -1

        for note in notes:
            self.set_draw_instructions(note)
            note.draw()
            self.add_widget(note)

    # Method for setting note drawing instructions and calling supplementary lines method
    def set_draw_instructions(self, note):
        note_name = midi2note(note.pitch)
        note.pos_x = self.get_x(note)
        note.sharp = '#' in note_name
        note.pos_y = self.get_y(note_name)
        note.upper = note.pos_y > self.third_line
        self.complete_lines(note)

    # Method for setting x-coord of note. Assumes notes are sent in onset order and equally spaces them
    def get_x(self, note):
        if note.start > self.current_onset:
            x = self.current_x + self.width * 0.03
            self.current_x = x
            self.current_onset = note.start
        else:
            x = self.current_x
        return x

    # Method for finding y-coord of note. note_string should be given as string in the format of midi2note
    def get_y(self, note_string):
        note = note_string[0]
        octave = int(note_string[-1])

        note_y = self.note_letters.index(note) * self.line_separation/2
        # Bass Key
        if 0 <= octave and octave <= 3:
            octave_y = self.bass_octaves.index(octave) * len(self.note_letters) * self.line_separation/2
            y = note_y + octave_y + self.lower_note_bass
            self.set_key(treble = False)
        else:
            octave_y = self.treble_octaves.index(octave) * len(self.note_letters) * self.line_separation/2
            y = note_y + octave_y + self.lower_note_treble
            self.set_key(treble = True)
        return y

    # Method for drawing supplementary lines
    def complete_lines(self, note):
        if note.pos_y >= self.first_line + self.line_separation:
            y = self.first_line + self.line_separation
            while y <= note.pos_y:
                with self.canvas.after:
                    Color(0,0,0)
                    Line(points = [note.pos_x - 10, y, note.pos_x + 10, y], width = note.line_width)
                y += self.line_separation
        if note.pos_y <= self.fifth_line - self.line_separation:
            y = self.fifth_line - self.line_separation
            while y >= note.pos_y:
                with self.canvas.after:
                    Color(0,0,0)
                    Line(points = [note.pos_x - 10, y, note.pos_x + 10, y], width = note.line_width)
                y -= self.line_separation

    # Method for saving lines for drawing supplementary lines eventually
    def set_key(self, treble):
        if treble:
            self.first_line = self.first_line_treble
            self.third_line = self.third_line_treble
            self.fifth_line = self.fifth_line_treble
        else:
            self.first_line = self.first_line_bass
            self.third_line = self.third_line_bass
            self.fifth_line = self.fifth_line_bass


class StaveLayout(BoxLayout):
    """
    Widget for drawing the stave. Also based on https://github.com/Syncrossus/Perfect-Melody/blob/master/gui/scorewidget.py
    Is merely a constructor for the layout present in the kv file
    """
    pass

class ScoreLayout(BoxLayout):
    """
    Method for managing which measures are displayed and which notes are highlighted
    """

    # Constants
    notes_in_screen = 30 # Adjust parameter after testing on several .mid files

    def __init__(self, midi, switcher, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.score = ScoreWidget(midi, switcher)
        self.stave = StaveLayout()
        self.measure = self.stave.children[0]
        self.add_widget(self.stave)
        self.notes_to_display = self.score.notes.copy()
        Clock.schedule_once(self.display_notes, 10)

    def print_current_notes(self):
        for note in self.score.current_notes:
            print('Pitch: {}, Start Time: {:.2f}, End Time: {:.2f}, Duration: {}'.format(note.pitch, note.start, note.end, note.duration))

    # Method for popping out notes needing to be displayed and displaying them
    def display_notes(self, dt):
        count = 0
        notes = []
        current_onset = -1
        while (count < self.notes_in_screen) and self.notes_to_display:
            note = self.notes_to_display.pop(0)
            notes.append(note)
            if note.start > current_onset:
                count +=1
                current_onset = note.start
            # print('Pitch: {}, Start Time: {:.2f}, Count: {}'.format(note.pitch, note.start, count)) # Debug
        self.measure.display(notes)

    def close(self):
        self.score.close()

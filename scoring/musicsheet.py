# Create songbox widget to be added to main.
# To do: first version of musical drawing

# Step 1: Until 30/04 -> Working first version
# Current stage -> Toggling notes method not working. Try scrolling line
# TO DO:
# 1) Adapt position to get x-coord for notes
# 2) Create method for drawing line
# 3) Auto-update line

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
        if self.switcher.is_playing() == True:
            self.update_current_notes() # Update current notes
            for note in self.current_notes:
                print('Pitch: {}, Start Time: {:.2f}, End Time: {:.2f}, Duration: {}'.format(note.pitch, note.start, note.end, note.duration))
            print('----------------------///////////----------------------------') # Debug
            self.highlight_notes() # Turn all notes on

    # Method for highlighting active notes
    def highlight_notes(self):
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

    # Method for erasing all notes drawn
    def erase(self, notes):
        self.canvas.after.clear()
        for note in notes:
            self.remove_widget(note)


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
    correction = 15 # Amount of notes to disconsider when updating stave

    def __init__(self, midi, switcher, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.score = ScoreWidget(midi, switcher)
        self.stave = StaveLayout()
        self.measure = self.stave.children[0]
        self.add_widget(self.stave)
        self.notes_being_displayed = []
        self.notes_to_display = []
        self.note_index = 0
        self.update_clock = None
        Clock.schedule_once(self.first_display, 10)


    # Method for displaying the notes that are going to be played
    def display_notes(self):
        notes = self.get_notes_to_display()
        self.measure.display(notes)
        self.notes_being_displayed = notes

    # Method for getting notes to be displayed
    def get_notes_to_display(self):
        space_count = 0 # variable for counting how many spaces were used
        prev_idx = self.note_index-self.correction # Variable to store where previous score frame was with a correction to disconsider transition notes
        notes = []
        current_onset = -1
        while (space_count < self.notes_in_screen) and (self.note_index < len(self.score.notes)):
            note = self.score.notes[self.note_index]
            notes.append(note)
            if note.start > current_onset:
                space_count +=1
                current_onset = note.start
            self.note_index += 1
        if self.note_index == len(self.score.notes): # If song has finished set the counter to zero
            self.note_index = 0
            self.notes_to_display = self.score.notes[:prev_idx] # and determine first notes as the ones to show
        else:
            self.notes_to_display = self.score.notes[self.note_index:] # If the song is going on, use next notes as notes to display
        return notes

    def update_display(self, dt):
        if not set(self.notes_to_display).isdisjoint(self.score.current_notes):
            self.measure.erase(self.notes_being_displayed)
            self.display_notes()

    def first_display(self, dt):
        self.display_notes()
        sample_interval = self.score.switcher.players[0].chunk # In case of parameter customization, think about changing
        fs = self.score.switcher.players[0].file.getframerate() # these two variables to attributes to hop_size and fs
        self.update_clock = Clock.schedule_interval(self.update_display, sample_interval/fs)

    def close(self):
        self.score.close()
        Clock.unschedule(self.update_clock)

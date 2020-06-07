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
        self.previous_notes = [] # List used to see which notes were lastly played so that they can be toggled off
        self.switcher = switcher # Corresponding switcher

        # Use of Kivy clock to schedule update of current notes
        sample_interval = self.switcher.players[0].chunk # In case of parameter customization, think about changing
        fs = self.switcher.players[0].file.getframerate() # these two variables to attributes to hop_size and fs
        self.clock = Clock.schedule_interval(self.callback, sample_interval/fs)

    # Method for highlighting notes currently being played
    def callback(self, dt):
        """
        Callback method responsible for updating current notes, and highlighting notes being played
        :param dt: Standard param for callbacks in Kivy
        """
        if self.switcher.is_playing() == True:
            self.update_current_notes() # Update current notes
            # for note in self.current_notes:
            #     print('Pitch: {}, Start Time: {:.2f}, End Time: {:.2f}, Duration: {}'.format(note.pitch, note.start, note.end, note.duration))
            # print('----------------------///////////----------------------------') # Debug
            self.highlight_notes() # Turn all notes on

    # Method for highlighting active notes
    def highlight_notes(self):
        """"
        This method checks if notes are not anymore in current notes, so they can be toggled off
        And also checks if there are new notes in current notes, so that they can be toggled on
        """
        for previous_note in self.previous_notes:
            if previous_note not in self.current_notes:
                previous_note.toggle()
        for current_note in self.current_notes:
            if current_note not in self.previous_notes:
                current_note.toggle()

    # Method for updating active notes
    def update_current_notes(self):
        """
        This method updates notes currently being played. For this we use the alignment with the MIDI generated .wav.
        Given an origin frame for the current audio, we find the equivalent frame in the Midi, and get the active notes
        in this equivalent frame. There are errors due to the alignment, and those can be seen on a note-level scale.
        """
        origin = self.switcher.players.index(self.switcher.currentPlayer) # Check in which audio I am
        origin_frame = self.switcher.currentPlayer.get_frame() # original frame for current player
        if origin == 0: # If in MIDI corresponding .wav file, get current frame
            frame = origin_frame
        else: # Else get corresponding frame
            frame = self.switcher.get_corresponding_frame(origin, 0, origin_frame, method = 'avg')
        self.previous_notes = self.current_notes # Update previous notes for correct toggling on and off
        self.current_notes = get_active_notes(self.notes, frame) # Update current notes with this function

    # Method for closing scheduled callbacks
    def close(self):
        Clock.unschedule(self.clock)

class MeasureWidget(FloatLayout):
    """
    Widget for drawing a measure. Largely based on the work in https://github.com/Syncrossus/Perfect-Melody/blob/master/gui/scorewidget.py
    Should contain all required methods for drawing a measure
    """

    # Constants
    # These are mainly drawing instructions for the measure displayed in the stave widget.
    # They can be arbitrarely changed to fit design requirements
    start_line_treble = 150 # Instruction on where to start drawing treble clef
    start_line_bass = 270 # Instruction on where to star drawing bass clef
    line_separation = 15 # Separation between pentagram lines
    note_letters = 'CDEFGAB' # Constants for recognizing note names. Was made according to the functions in midread
    bass_octaves = [0, 1, 2, 3] # Octaves drawn in bass clef
    treble_octaves = [4, 5, 6, 7, 8] # Octaves drawn in treble clef

    # Observation: Drawings were considered for piano sheet music. Being so, the highest note is C8 and the lowest
    # is A0.

    def display(self, notes):

        # Constants that depend on the MeasureWidget.
        # Kivy only accepts references such as .top after the widget is displayed. Since the drawing depend heavily
        # on these relative position instructions, it is necessary to schedule functions for drawing to after the
        # initialization of the widget. Try to find a better workaround later
        self.first_line_treble = self.top - self.start_line_treble # First line of treble pentagram
        self.third_line_treble = self.first_line_treble - self.line_separation * 2 # 3rd line
        self.fifth_line_treble = self.third_line_treble - self.line_separation * 2 # 5th line
        # Lowest note of treble key is central C
        self.lower_note_treble = self.fifth_line_treble - self.line_separation # Position of central C in the stave

        self.first_line_bass = self.top - self.start_line_bass # First line of bass pentagram
        self.third_line_bass = self.first_line_bass - self.line_separation * 2 # 3rd line
        self.fifth_line_bass = self.third_line_bass - self.line_separation * 2 # 5th line
        # Lowest line of bass key minus one octave and one note minus 5 notes -> A0
        self.lower_note_bass = self.fifth_line_bass - (self.line_separation * 4 + self.line_separation * 5)

        self.current_x = self.x + self.width * 0.04 # Position for first note. 0.04 of width is arbitrary. Change hardcode later
        self.current_onset = -1 # initialization of current onset variable. Used to see if note is drawn ate the same x ad current note

        for note in notes: # for every note -> draw note
            self.set_draw_instructions(note)
            note.draw()
            self.add_widget(note) # every note is a widget that can be manipulated

    # Method for setting note drawing instructions and calling supplementary lines method
    def set_draw_instructions(self, note):
        note_name = midi2note(note.pitch) # Finding note name -> Ex: C#5, A4, ...
        note.pos_x = self.get_x(note) # Get x-coord for note
        note.sharp = '#' in note_name # Find out if it has alteration
        note.pos_y = self.get_y(note_name) # Get note y-coord according to note name
        note.upper = note.pos_y > self.third_line # If note is above the third line, it must be drawn with "leg" downward
        self.complete_lines(note) # Method for drawing auxiliary lines

    # Method for setting x-coord of note. Assumes notes are sent in onset order and equally spaces them
    def get_x(self, note):
        """
        This method takes a note and finds out its x-coord. For the moment it equally spaces all notes
        :param note: NoteWidget
        """
        if note.start > self.current_onset: # If note starts after the current note
            x = self.current_x + self.width * 0.03 # Place it to the right of the current one. 0.03 is arbitrary
            self.current_x = x # Update current x-coord fur future notes.
            self.current_onset = note.start # Update current to find out if notes are after or at the same time  as current note
        else: # If note is happening at the same time
            x = self.current_x # Use current x-coord
        return x

    # Method for finding y-coord of note. note_string should be given as string in the format of midi2note
    def get_y(self, note_string):
        """
        Method for getting note y-coord
        :param note_string: String with note name on midread format, e.g. C#6
        """
        note = note_string[0] # Note name always comes first
        octave = int(note_string[-1]) # Octave is always last digit
        # Alterations do not need to be considered for y-coord

        note_y = self.note_letters.index(note) * self.line_separation/2 # Height corresponding to note
        # Bass Key
        if 0 <= octave and octave <= 3: # if note is on bass clef, get height for octave based on that
            octave_y = self.bass_octaves.index(octave) * len(self.note_letters) * self.line_separation/2
            y = note_y + octave_y + self.lower_note_bass
            self.set_key(treble = False) # Method for telling widget if note is bass or treble. Used by auxiliary lines
        else: # Same thing for treble clef
            octave_y = self.treble_octaves.index(octave) * len(self.note_letters) * self.line_separation/2
            y = note_y + octave_y + self.lower_note_treble
            self.set_key(treble = True)
        return y

    # Method for drawing auxiliary lines
    def complete_lines(self, note):
        if note.pos_y >= self.first_line + self.line_separation: # Only draw line for notes at least one line above stave
            y = self.first_line + self.line_separation
            while y <= note.pos_y:
                with self.canvas.after: # Drawing instructions for repeatedly drawing lines while note height is not reached
                    Color(0,0,0)
                    Line(points = [note.pos_x - 10, y, note.pos_x + 10, y], width = note.line_width)
                y += self.line_separation
        if note.pos_y <= self.fifth_line - self.line_separation: # Or one line below
            y = self.fifth_line - self.line_separation
            while y >= note.pos_y:
                with self.canvas.after: # Same for notes below stave
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
    notes_in_screen = 30 # Number of notes that fit one "page" of measure widget. Adjust parameter after testing on several .mid files
    correction = 15 # Amount of notes to disconsider when updating stave. Needed because border notes can remain in current notes list

    def __init__(self, midi, switcher, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.score = ScoreWidget(midi, switcher) # Score object used for getting notes
        self.stave = StaveLayout()
        self.measure = self.stave.children[0] # Measure widget for drawing notes. Child of stave
        self.add_widget(self.stave)
        self.notes_being_displayed = [] # Notes currently displayed
        self.notes_to_display = [] # Notes that need to be displayed from next "page" onward
        self.note_index = 0 # Which note was the last one drawn
        self.update_clock = None # callback Kivy clock. Initialized later.
        Clock.schedule_once(self.first_display, 30) # Wait to draw notes for the first time due to use of relative positions


    # Method for displaying the notes that are going to be played
    # Simply calls other functions to find out notes to display, to display them, and updates notes_being_displayed
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
        # While there is space in the screen and while there are notes to draw, save note for drawing
        while (space_count < self.notes_in_screen) and (self.note_index < len(self.score.notes)):
            note = self.score.notes[self.note_index]
            notes.append(note) # Save note for drawing
            if note.start > current_onset: # If the note is played at the same time as the las one, together they do not occupy more horizontal space on the screen
                space_count +=1 # However, if the note is played after the last one, we must count the space it will occupy
                current_onset = note.start
            self.note_index += 1 # Attribute to save note where drawing has stopped
        if self.note_index == len(self.score.notes): # If song has finished set the counter to zero
            self.note_index = 0
            self.notes_to_display = self.score.notes[:prev_idx] # and determine first notes as the ones to show
        else:
            self.notes_to_display = self.score.notes[self.note_index:] # If the song is going on, use next notes as notes to display
        return notes

    def update_display(self, dt):
        """
        Method for updating notes displayed in screen
        :param dt: Standard Kivy clock callback param
        """
        # If there are notes being played that are yet to be displayed
        if not set(self.notes_to_display).isdisjoint(self.score.current_notes):
            self.measure.erase(self.notes_being_displayed) # Erase notes on screen
            self.display_notes() # and display the new ones

    def first_display(self, dt):
        """
        Auxiliary method for displaying notes for the first time. Used because Kivy relative positions need to wait
        widget initialization
        :param dt: Standard Kivy clock callback param
        """
        self.display_notes()
        sample_interval = self.score.switcher.players[0].chunk # In case of parameter customization, think about changing
        fs = self.score.switcher.players[0].file.getframerate() # these two variables to attributes to hop_size and fs
        self.update_clock = Clock.schedule_interval(self.update_display, sample_interval/fs)

    def close(self):
        self.score.close()
        Clock.unschedule(self.update_clock)

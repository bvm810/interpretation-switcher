from mido import MidiFile
from mido import tick2second
from mido import second2tick
from midi2audio import FluidSynth
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line

# Note class for facilitating midi parsing
class NoteWidget(Widget):

    # Constants
    diameter = 10
    line_width = 1.3

    def __init__(self, pitch, start, **kwargs):
        super().__init__(**kwargs)
        self.pitch = pitch # MIDI note pitch
        self.start = start # Starting time
        self.end = 0
        self.duration = None # Duration in multiple of 1/128th note
        self.pos_x = 0 # x-coord position
        self.pos_y = 0 # y-coord position
        self.highlight = 0 # flag to show if note is jighlighted or not
        self.upper = None # upper or lower part of stave

    # Method for drawing a single note
    def draw(self):
        with self.canvas:
            Color(self.highlight,0,0)
            Ellipse(pos = (self.pos_x-self.diameter/2, self.pos_y-self.diameter/2), size = (self.diameter, self.diameter))
            if self.upper == True:
                x_coord = self.pos_x - self.diameter/2
                y_coord = self.pos_y - self.diameter/2 + self.diameter/2
                Line(points = [x_coord, y_coord, x_coord, y_coord - 25], width = self.line_width)
            else:
                x_coord = self.pos_x - self.diameter/2 + self.diameter
                y_coord = self.pos_y - self.diameter/2 + self.diameter/2
                Line(points = [x_coord, y_coord, x_coord, y_coord + 25], width = self.line_width)

    # Method for highlighting a specific note
    def toggle(self):
        self.highlight = 1 - self.highlight
        self.draw()



# Converting .mid file to .wav to avoid depending on external converters
def midi2wav(filename):
    fs = FluidSynth()
    fs.midi_to_audio(filename+'.mid', filename+' MIDI.wav')

# Function for converting midinumber to note
def midi2note(midinumber):
    notes = {0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E', 5: 'F', 6: 'F#', 7: 'G', 8: 'G#', 9: 'A', 10: 'A#', 11: 'B'}
    octave = str(midinumber // 12)
    note = notes[midinumber % 12]
    return note + octave

# print(midi2note(69))

# Parses .mid to get all notes with its times of beginning and end and duration in beats
def get_notes(filename):
    mid = MidiFile(filename)
    tempo = 500000
    elapsed_time = 0 # in seconds
    quarter_note_duration = mid.ticks_per_beat
    shortest_note = quarter_note_duration/8
    notes = []
    for track in mid.tracks:
        for msg in track:
            if not msg.is_meta:
                elapsed_time += tick2second(msg.time, quarter_note_duration, tempo)
            if msg.type == 'set_tempo':
                tempo = msg.tempo
            if msg.type == 'note_on':
                notes.append(NoteWidget(msg.note, elapsed_time))
            if msg.type == 'note_off':
                for note in notes:
                    if note.pitch == msg.note and note.duration == None:
                        # duration of note in multiple of 1/128th note
                        note.duration = round((second2tick(elapsed_time, quarter_note_duration, tempo) - second2tick(note.start, quarter_note_duration, tempo))/shortest_note)
                        note.end = elapsed_time
                        break
    return notes

# notes = get_notes('/Users/bernardo/Documents/Projetos em Andamento/Projet Long S7+S8/interpretation-switcher/scoring/Chopin Prelude Op. 28 No. 7.mid')
# for note in notes:
#     print('Pitch: {}, Start Time: {:.2f}, End Time: {:.2f}, Duration: {}'.format(note.pitch, note.start, note.end, note.duration))

# Gets active notes for a given frame
def get_active_notes(notes, frame, hop_size = 2048, fs = 44100):
    start_time = (frame * hop_size)/fs
    end_time = (frame * hop_size + 2 * hop_size)/fs
    active_notes = [note for note in notes if (not ((note.end <= start_time) or (note.start >= end_time)))]
    return active_notes

# notes = get_notes('./Chopin Prelude Op. 28 No. 7.mid')
# for note in notes:
#     print('Pitch: {}, Start Time: {:.2f}, End Time: {:.2f}, Duration: {}'.format(note.pitch, note.start, note.end, note.duration))
# active_notes = get_active_notes(notes, 52)
# for note in active_notes:
#     print('Pitch: {}, Start Time: {:.2f}, End Time: {:.2f}, Duration: {}'.format(note.pitch, note.start, note.end, note.duration))

from mido import MidiFile
from mido import tick2second
from mido import second2tick
from midi2audio import FluidSynth
# Parse Midi and get note, onset in frames, onset in beats, and duration in beats
# Invert dict to have dict of key = frame and value = note index
# Create function to draw all notes parsed

class Note:
    def __init__(self, pitch, start):
        self.pitch = pitch # MIDI note pitch
        self.start = start # Starting time
        self.end = 0
        self.duration = None # Duration in multiple of 1/128th note

def midi2wav(filename):
    fs = FluidSynth()
    fs.midi_to_audio(filename+'.mid', filename+' MIDI.wav')

def getNotes(filename):
    mid = MidiFile(filename)
    tempo = 500000
    elapsed_time = 0 # in seconds
    quarter_note_duration = mid.ticks_per_beat
    shortest_note = quarter_note_duration/32
    notes = []
    for track in mid.tracks:
        for msg in track:
            if not msg.is_meta:
                elapsed_time += tick2second(msg.time, quarter_note_duration, tempo)
            if msg.type == 'set_tempo':
                tempo = msg.tempo
            if msg.type == 'note_on':
                notes.append(Note(msg.note, elapsed_time))
            if msg.type == 'note_off':
                for note in notes:
                    if note.pitch == msg.note and note.duration == None:
                        # duration of note in multiple of 1/128th note
                        note.duration = round((second2tick(elapsed_time, quarter_note_duration, tempo) - second2tick(note.start, quarter_note_duration, tempo))/shortest_note)
                        note.end = elapsed_time
                        break
    return notes

# notes = getNotes('/Users/bernardo/Documents/Projetos em Andamento/Projet Long S7+S8/interpretation-switcher/scoring/Chopin Prelude Op. 28 No. 7.mid')
# for note in notes:
#     print('Pitch: {}, Start Time: {:.2f}, End Time: {:.2f}, Duration: {}'.format(note.pitch, note.start, note.end, note.duration))

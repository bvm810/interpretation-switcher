import pyaudio
import wave
import time

class AudioPlayer():

    def __init__(self, filename):
        self.is_playing = False
        self.currentSample = 0
        self.chunk = 1024
        self.file = wave.open(filename, 'rb')

        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(format=self.p.get_format_from_width(self.file.getsampwidth()),
                channels=self.file.getnchannels(),
                rate=self.file.getframerate(),
                output=True)

    def play(self):
        self.is_playing = True

    def pause(self):
        self.is_playing = False

    def callback(self):
        data = self.file.readframes(self.chunk)

        if len(data) <= 0:
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()

        if self.is_playing == True:
            self.stream.write(data)

a = AudioPlayer('Chopin Prelude Op. 28 No. 7 N. Freire.wav')
a.play()
time.sleep(5)
a.pause()
a.play()

import pyaudio
import wave
import time

class AudioPlayer():

    def __init__(self, filename):
        self.is_playing = False
        self.currentSample = 0
        self.file = wave.open(filename, 'rb')

        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(format=self.p.get_format_from_width(self.file.getsampwidth()),
                channels=self.file.getnchannels(),
                rate=self.file.getframerate(),
                output=True,
                stream_callback=self.callback)

    def play(self):
        self.stream.start_stream()
        self.is_playing = True

        # while self.stream.is_active():
        #     time.sleep(0.1)

    def pause(self):
        self.stream.stop_stream()
        self.is_playing = False

        # self.stream.close()
        # self.file.close()
        #
        # self.p.terminate()


    def callback(self, in_data, frame_count, time_info, status):
        data = self.file.readframes(frame_count)
        return (data, pyaudio.paContinue)

a = AudioPlayer('Chopin Prelude Op. 28 No. 7 N. Freire.wav')
a.play()
time.sleep(5)
a.pause()
a.play()

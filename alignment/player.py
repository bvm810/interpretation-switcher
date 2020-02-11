import pyaudio
import wave
import time
from pynput import keyboard

def audioplayer(filename):
    paused = False    # nonlocal to track if the audio is paused

    # def pause(key):
    #     nonlocal paused
    #     print (key)
    #     if key == keyboard.Key.space:
    #         if stream.is_stopped():     # time to play audio
    #             print ('play pressed')
    #             stream.start_stream()
    #             paused = False
    #
    #         elif stream.is_active():   # time to pause audio
    #             print ('pause pressed')
    #             stream.stop_stream()
    #             paused = True

    def on_press(key):
        print('{0} pressed'.format(key))


    wf = wave.open('/Users/bernardo/Documents/Projetos em Andamento/Projet Long S7+S8/interpretation-switcher/alignment/'+filename, 'rb')
    p = pyaudio.PyAudio()

    def callback(in_data, frame_count, time_info, status):
        data = wf.readframes(frame_count)
        return (data, pyaudio.paContinue)

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
                stream_callback=callback)

    stream.start_stream()
    while stream.is_active() or paused==True:
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()
        time.sleep(0.1)

    stream.stop_stream()
    stream.close()
    wf.close()

    p.terminate()

song1 = audioplayer('Chopin Prelude Op. 28 No. 7 N. Freire.wav')

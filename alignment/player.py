from pygame import mixer as mix
import time

def init_audioplayer(filelist, frequency = 44100, size = -16, channels = 2, buffer = 512):
    """
    Function for initializing pygame's mixer module with the desired wav files in its channels.

    :param filelist: List of strings with filenames of audiofiles to be aligned
    :return channel_list: List of Channel objects tuples to be manipulated with play/pause
    """
    mix.init(frequency=frequency, size=size, channels=channels, buffer=buffer)
    channel_list = []
    for name in filelist:
        sound = mix.Sound(name)
        channel = mix.Channel(filelist.index(name))
        channel.play(sound)
        channel.pause()
        channel_list.append(channel)
    return channel_list

# Test
filenames = ['Chopin Prelude Op. 28 No. 7 M. Pollini.wav', 'Chopin Prelude Op. 28 No. 7 MIDI.wav', 'Chopin Prelude Op. 28 No. 7 N. Freire.wav']
channel_list = init_audioplayer(filenames)
for channel in channel_list:
    channel.unpause()
    time.sleep(10)
    channel.pause()

from librosa.core import load

def load_file(filename):
    """
    Function for loading audio file with librosa already with desired params (same sampling rate and conversion to mono)

    :param filename: path of the file to be loaded
    :return y: numpy array of samples
            sr: sampling rate
    """
    y, sr = load(filename, sr = None, mono = True)
    return y, sr


# Test plotting
from librosa.display import waveplot
import matplotlib.pyplot as plt

x, fs = load_file('Chopin Prelude Op. 28 No. 7 N.Freire.wav')
plt.figure(figsize=(16, 4))
waveplot(x, sr=fs)
plt.title('Test Plot $X$')
plt.tight_layout()

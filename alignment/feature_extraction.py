from librosa.feature import chroma_stft

def chroma(audio, fs, norm = 2, n_fft = 4096, hop_length = 2048, win_length = 4096, window = 'hamming', center = False):
    """
    Function for extracting chroma features using librosa implementation

    :param: Same as in librosa. See librosa.feature.chroma_stft for details.
    :return: Chroma features for each window in matrix form
    """

    chromagram = chroma_stft(audio,
                             fs,
                             norm = norm,
                             n_fft = n_fft,
                             hop_length = hop_length,
                             win_length = win_length,
                             window = window,
                             center = center
                             )
    return chromagram

# # Test plotting
# from librosa.display import specshow
# import matplotlib.pyplot as plt
# from setup import load_file
#
#
# x, fs = load_file('Chopin Prelude Op. 28 No. 7 MIDI.wav')
# chromagram = chroma(x, fs)
#
# plt.figure(figsize = (8,4))
# specshow(chromagram, x_axis='time', y_axis='chroma', cmap='gray_r', hop_length=2048)
# plt.title('Chroma Representation')
# plt.colorbar()
# plt.tight_layout()
# plt.show()

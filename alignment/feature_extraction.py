from librosa.feature import chroma_stft
import numpy as np

def chroma(audio, fs, norm = 2, n_fft = 4096, hop_length = 2048, win_length = 4096, window = 'hamming', center = False, epsilon = 0.0001, gamma = 10):
    """
    Function for extracting chroma features using librosa implementation.
    It also applies normalization and compression as in Muller's book.

    :param: For all except epsilon, same as in librosa. See librosa.feature.chroma_stft for details
    :param epsilon: Silence threshold. If the norm on a given frame is smaller than epsilon, replaces by norm 1 vector.
    :return chromagram: Chroma features for each window in matrix form
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

    # Normalization
    for column in chromagram.T:
        if np.linalg.norm(column, 2) < epsilon:
            column[...] = (1/np.sqrt(12)) * np.ones(12)

    # Compression
    chromagram = np.log10(1+gamma*chromagram)

    return chromagram

# Test plotting
# from librosa.display import specshow
# import matplotlib.pyplot as plt
# from setup import load_file
#
#
# x, fs = load_file('Chopin Prelude Op. 28 No. 7 N. Freire.wav')
# chromagram = chroma(x, fs)
#
# print(chromagram[:, 1180])
#
# plt.figure(figsize = (8,4))
# specshow(chromagram, x_axis='time', y_axis='chroma', cmap='gray_r', hop_length=2048)
# plt.title('Chroma Representation')
# plt.colorbar()
# plt.tight_layout()
# plt.show()

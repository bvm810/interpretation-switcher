from librosa.sequence import dtw
from alignment.setup import load_file
from alignment.feature_extraction import chroma
import numpy as np

def dtw_align(audio1, audio2, metric = 'cosine', step_sizes_sigma = None, weights_add = None, weights_mul = None, global_constraints = False, band_rad = 0.25):
    """
    Function for aligning using DTW implementation by librosa. All arguments are the same except step_sizes and weights
    The length of those three parameters must be the same, otherwise librosa will raise an error.

    :param step_sizes_sigma: List of possible step sizes. Indicates which previous cells of D to use when dynamically calculating new cells of D
    :param weights_add: List of additive weights for each of the step_sizes
    :param weights_mul: List of multiplicative weights for each of the step sizes
    :return D, wp: Cost matrix and warping path
    """
    if step_sizes_sigma is None:
        step_sizes_sigma = np.asarray([(1,1), (1,0), (0,1)])

    if weights_add is None:
        weights_add = np.asarray([0, 0, 0])

    if weights_mul is None:
        weights_mul = np.asarray([1, 1, 1])

    D, wp = dtw(X = audio1,
                Y = audio2,
                metric = metric,
                step_sizes_sigma = step_sizes_sigma,
                weights_add = weights_add,
                weights_mul = weights_mul,
                global_constraints = global_constraints,
                band_rad = band_rad)
    return D, wp

# # Test plotting for dtw_align
# from librosa.display import specshow
# import matplotlib.pyplot as plt
# from setup import load_file
# from feature_extraction import chroma
#
#
# x, fs_x = load_file('Chopin Prelude Op. 28 No. 7 N. Freire.wav')
# y, fs_y = load_file('Chopin Prelude Op. 28 No. 7 MIDI.wav')
#
# if (fs_x != fs_y):
#     print("Error: .wav files do not have the same sampling frequency")
#     exit()
#
# fs = fs_x
# audio1 = chroma(x, fs)
# audio2 = chroma(y, fs)
#
# D, wp = dtw_align(audio1, audio2)
# wp_s = np.asarray(wp) * 2048/fs
#
# fig = plt.figure(figsize=(6,6))
# ax = fig.add_subplot(1,1,1)
# specshow(D, x_axis='s', y_axis='s', cmap='gray_r', sr = fs, hop_length=2048)
# imax = ax.imshow(D, cmap=plt.get_cmap('gray_r'), origin='lower', interpolation='nearest', aspect='auto')
# ax.plot(wp_s[:, 1], wp_s[:, 0], color='r', marker='o', markersize = 1)
# plt.title('Warping Path on Acc. Cost Matrix $D$')
# plt.colorbar()
# plt.show()

def warp(filename1, filename2):
    """
    Function for obtaining warping path based only on filenames
    OBS: Still does not support change in parameters for chroma and dtw_align
    :param filename1: filename of first audio
    :param filename2: filename of second audio
    :return wp: warping path
    """
    x, fs_x = load_file(filename1)
    y, fs_y = load_file(filename2)

    if fs_x != fs_y:
        return None

    fs = fs_x
    audio1 = chroma(x, fs)
    audio2 = chroma(y, fs)

    wp = dtw_align(audio1, audio2)[1]
    return wp

def align_audios(audios):
    """
    Function for aligning several audio files
    :param audios: list with filenames for the audios
    :return warp_dict: dict with tuple of indexes as key and warping path as value
    """
    warp_dict = {}
    for audio_i in audios:
        for audio_j in audios:
            ij_key = (audios.index(audio_i),audios.index(audio_j))
            ji_key = (audios.index(audio_j),audios.index(audio_i))
            if (audio_i != audio_j) and (ij_key not in warp_dict) and (ji_key not in warp_dict):
                wp = warp(audio_i, audio_j)
                warp_dict[(audios.index(audio_i),audios.index(audio_j))] = wp
                warp_dict[(audios.index(audio_j),audios.index(audio_i))] = np.column_stack((wp[:,1],wp[:,0]))

    return warp_dict


# Testing for warp_dict
# warp_dict = align_audios(['Chopin Prelude Op. 28 No. 7 MIDI.wav', 'Chopin Prelude Op. 28 No. 7 M. Pollini.wav', 'Chopin Prelude Op. 28 No. 7 N. Freire.wav'])
# works = True
# for key in warp_dict:
#     if not np.array_equal(warp_dict[(key[0], key[1])][:,0], warp_dict[(key[1], key[0])][:,1]):
#         works = False
#     if not np.array_equal(warp_dict[(key[0], key[1])][:,1], warp_dict[(key[1], key[0])][:,0]):
#         works = False
#
# print(works)


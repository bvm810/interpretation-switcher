from librosa.sequence import dtw
import numpy as np


# Fix chroma feature extraction to avoid NaN problem in DTW !

def dtw_align(audio1, audio2, metric = 'cosine', step_sizes_sigma = None, weights_add = None, weights_mul = None, global_constraints = False, band_rad = 0.25):
    """
    Function for aligning using DTW implementation by librosa. All arguments are the same except step_sizes and weights
    The length of those three parameters must be the same, otherwise librosa will raise an error.

    :param step_sizes_sigma: List of possible step sizes. Indicates which previous cells of D to use when dynamically calculating new cells of D
    :param weights_add: List of additive weights for each of the step_sizes
    :param weights_mul: List of multiplicative weights for each of the step sizes
    :return:
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

# # Test plotting
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
# D, wp = dtw_align(audio1, audio2, metric = 'euclidean')
# wp_s = np.asarray(wp) * 2048/fs
#
# fig = plt.figure(figsize=(6,6))
# ax = fig.add_subplot(1,1,1)
# specshow(D, x_axis='s', y_axis='s', cmap='gray_r', sr = fs, hop_length=2048)
# imax = ax.imshow(D, cmap=plt.get_cmap('gray_r'), origin='lower', interpolation='nearest', aspect='auto')
# ax.plot(wp_s[:, 1], wp_s[:, 0], marker='o', color='r')
# plt.title('Warping Path on Acc. Cost Matrix $D$')
# plt.colorbar()
# plt.show()



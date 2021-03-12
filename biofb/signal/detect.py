""" Function collection for (simple) feature detection in signals. """
import numpy as np
from scipy import signal


def find_peaks(x: np.ndarray, distinction_range: float = 0.75):
    """Finds peaks whose values are `>= distinction_range * (|mean - min|)` of the data)

    :param x: Data subjected to peak finding (array_like).
    :param distinction_range: Distinction range which identifies peaks by (positive) value (float).
    :return: Tuple of (list of probable peaks, list of possible peaks)
    """

    x = np.asarray(x)
    possible_peaks = signal.find_peaks(x)[0]
    peak_values = x[possible_peaks]
    probable_peaks = peak_values > (distinction_range*(np.absolute(np.mean(x, axis=-1) - np.min(x, axis=-1))))

    return possible_peaks[probable_peaks], possible_peaks


def check_peaks(x: np.ndarray, peak_window: (int, None) = None, peaks: (np.ndarray, None) = None, **kwargs):
    """Checks whether `peaks` indices `pi` in `x` correspond to absolute maximum
       within running window `[pi-peak_window//2:pi-peak_window//2`]

    :param x: Data subjected to peak checking (array_like).
    :param peak_window: Running peak window which is used for to identify absolute maximum
                        (Optional int,
                         defaults to None -> `len(x)` is used as window).
    :param peaks: Possible peaks within data range
                  (Optional array_like,
                   defaults to None -> `preprocessing.find_peaks` is called on `x` and `**kwargs`).
    :TODO: Taken into consideration the list of previously detected probable peaks, a set of additional criteria
           were defined by Pan and Tompkins, in order to exclude peaks from the list of probable peaks.
    :return: Numpy-array containing indices of absolute maxima in `x` in running-`peak_window`
    """

    x = np.asarray(x)
    n_x = len(x)
    peak_window = peak_window if peak_window is not None else n_x
    pw_half = int(max([peak_window//2, 1]))

    peaks = peaks if peaks is not None else find_peaks(x, **kwargs)[0]
    definite_peaks = [
        max(x[int(max([0, pi - pw_half])):int(min([n_x, pi + pw_half]))]) == x[pi]
        for pi in peaks
    ]

    return np.asarray(peaks)[definite_peaks] if len(definite_peaks) > 0 else np.asarray([])

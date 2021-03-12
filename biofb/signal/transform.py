""" Function collection for signal transformations. """
import numpy as np
from scipy.fftpack import fft, fftfreq


def fast_fourier_transform(x: np.ndarray, sampling_rate: int, positive_axis=True, window: (bool, callable) = False, dB=False, **kwargs):
    """Perform fast Fourier transform of data, `x`, acquired with a specific `sampling_rate`.

    :param x: Data to be transformed (array_like).
    :param sampling_rate: Digital sampling rate of the data in Hz (int).
    :param positive_axis: Boolean which controls whether only the positive frequency axis is returned (True on default).
    :param window: Window function applied to data to suppress rectification errors for a given time interval
                   (boolean, callable, defaults to True).
                   If `window==True`, the `numpy.blackman` window is used.
                   If a custom callable window is provided, it must be callable on the length `N=len(x)` of the data.
    :param dB: Boolean which specifies whether the returned units are given in deci Bell (defaults to False).
    :param kwargs: Forwarded keyword arguments to `scipy.fft.fft`.
    :return: Fourier transform of the data, `x`.
    """

    x = np.asarray(x)         # make sure, x is an ndarray
    N = x.shape[-1]           # number of data points (sampling stels)
    T = 1./sampling_rate  # sampling spacing

    P = kwargs.pop('period', None)  # TODO

    if window:
        if isinstance(window, bool):
            window = np.blackman

        assert hasattr(window, '__call__'), 'Window function must be callable on argument `x.shape[-1]`.'

        w = window(N)
        yf = fft(x*w, **kwargs)

    else:
        yf = fft(x, **kwargs)

    xf = fftfreq(N, T)

    if dB:
        yf /= (N/2.0)
        yf = 20. * np.log10(np.abs(yf / abs(yf).max()))

    if not positive_axis:
        return xf, yf

    return xf[:N//2], yf[0:N//2]

""" Function collection for filtering signals. """
import numpy as np
from scipy import signal


def notch(w0, Q=30., sampling_rate=2.0):
    """Notch filter based on `scipy.signal.iirnotch`

    :param w0: Frequency to remove from a signal
    :param Q: Dimensionless quality factor that characterizes notch filter -3 dB bandwidth `bw` relative to its center frequency, `Q = w0/bw`.
    :param sampling_rate: The sampling rate of the digital system.
    :return: Numerator (b) and denominator (a) polynomials of the IIR filter.
    """
    notch_filter = signal.iirnotch(w0, Q, sampling_rate)
    return notch_filter


def apply_notch(x, w0, Q=30., sampling_rate=2.0, filtfilt=False, **kwargs):
    """Apply notch filter based on `scipy.signal.iirnotch` to signal x

    :param x: Signal to be notched (array_like).
    :param w0: Frequency to remove from a signal.
    :param Q: Dimensionless quality factor that characterizes notch filter -3 dB bandwidth `bw` relative to its center frequency, `Q = w0/bw`.
    :param sampling_rate: The sampling rate of the digital system.
    :param filtfilt: Boolean specifying whether to use `scipy.signal.filtfilt` or `signal.lfilter` (defaults to False).
    :return: Numerator (b) and denominator (a) polynomials of the IIR filter.
    """
    b, a = notch(w0=w0, Q=Q, sampling_rate=sampling_rate)
    filtered = signal.lfilter(b, a, x, **kwargs) if not filtfilt else signal.filtfilt(b, a, x[::-1], **kwargs)[::-1]
    return filtered


def bandpass(N: int, Wn: np.ndarray, analog: bool = False, sampling_rate: (None, float) = None):
    """Bandpass `sos`-filter of `scipy.signal.butter` method

    :param N: The order of the filter (int).
    :param Wn: Lower and Upper critical frequency or frequencies specifying the bandpass frequencies (array_like).
               For digital units, `Wn` is the same units as `sampling_rate`.
    :param analog: Boolean, when True specifying whether to return an analog filter, otherwise a digital filter is returned.
    :param sampling_rate: The sampling frequency of the digital system (optional float).
    :return: `scipy.signal.butter` bandpass filter
    """

    filter = signal.butter(N, Wn, btype='bandpass', fs=sampling_rate, output='sos', analog=analog)
    return filter


def bandstop(N: int, Wn: np.ndarray, analog: bool = False, sampling_rate: (None, float) = None):
    """Bandstop `sos`-filter of `scipy.signal.butter` method

    :param N: The order of the filter (int).
    :param Wn: Lower and Upper critical frequency or frequencies specifying the bandstop frequencies (array_like).
               For digital units, `Wn` is the same units as `sampling_rate`.
    :param analog: Boolean, when True specifying whether to return an analog filter, otherwise a digital filter is returned.
    :param sampling_rate: The sampling frequency of the digital system (optional float).
    :return: `scipy.signal.butter` bandstop filter
    """

    filter = signal.butter(N, Wn, btype='bandstop', fs=sampling_rate, output='sos', analog=analog)
    return filter


def lowpass(N: int, Wn: float, analog: bool = False, sampling_rate: (None, float) = None):
    """Lowpass `sos`-filter of `scipy.signal.butter` method

    :param N: The order of the filter (int).
    :param Wn: Lower critical frequency or frequencies specifying the lowpass frequency (array_like).
               For digital units, `Wn` is the same units as `sampling_rate`.
    :param analog: Boolean, when True specifying whether to return an analog filter, otherwise a digital filter is returned.
    :param sampling_rate: The sampling frequency of the digital system (optional float).
    :return: `scipy.signal.butter` lowpass filter
    """

    filter = signal.butter(N, Wn, btype='lowpass', fs=sampling_rate, output='sos', analog=analog)
    return filter


def highpass(N: int, Wn: float, analog: bool = False, sampling_rate: (None, float) = None):
    """Highpass `sos`-filter of `scipy.signal.butter` method

    :param N: The order of the filter (int).
    :param Wn: Lower critical frequency or frequencies specifying the highpass frequency (array_like).
               For digital units, `Wn` is the same units as `sampling_rate`.
    :param analog: Boolean, when True specifies to return an analog filter, otherwise a digital filter is returned.
    :param sampling_rate: The sampling frequency of the digital system (optional float).
    :return: `scipy.signal.butter` highpass filter
    """

    filter = signal.butter(N, Wn, btype='highpass', fs=sampling_rate, output='sos', analog=analog)
    return filter


def apply_sos_filter(x: np.ndarray, N: int, Wn: (np.ndarray, int, float), analog: bool = False, sampling_rate: (None, float) = None, sos_filter='bandpass', return_filter=False, filtfilt=False, **kwargs):
    """`sos`-filter of `scipy.signal.butter` method

    :param x: Array_like signal.
    :param N: The order of the filter (int).
    :param Wn: Lower critical frequency, higher critical frequency or frequency-window defining the `sos_filter`-specific frequency domain (array_like).
               For digital units, `Wn` is the same units as `sampling_rate`.
    :param analog: Boolean, when True specifying whether to return an analog filter, otherwise a digital filter is returned.
    :param sampling_rate: The sampling frequency of the digital system (optional float).
    :param sos_filter: bandfilter type, must be one of ('bandpass', 'highpass', 'lowpass', 'bandstop'), defaults to 'bandpass'.
    :param filtfilt: Boolean specifying whether to use `scipy.signal.filtfilt` or `signal.lfilter` (defaults to False).
    :param return_filter: Boolean, when True specifies to return the filtered signal and the bandfilter, otherwise only the filtered signal is returned.
    :return: `scipy.signal.butter` highpass filter
    """

    assert sos_filter in ('bandpass', 'highpass', 'lowpass', 'bandstop'), "Filter must be one of must be one of ('bandpass', 'highpass', 'lowpass', 'bandstop')."

    filter_function = globals()[sos_filter]
    sos_filter = filter_function(N=N, Wn=Wn, analog=analog, sampling_rate=sampling_rate)

    filtered = signal.sosfilt(sos_filter, x, **kwargs) if not filtfilt else signal.sosfiltfilt(sos_filter, x[::-1], **kwargs)[::-1]

    if return_filter:
        return filtered, sos_filter

    return filtered

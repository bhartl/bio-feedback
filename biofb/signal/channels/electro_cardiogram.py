""" Function collection for Electro-Cardiography (ECG) analysis

References:

- [1] biosignalsplux ECG datasheet: <PROJECT-HOME>/doc/bioplux/sensors/Electrocardiography_(ECG)_Datasheet.pdf
- [2] biosignalsplux ECG user-manual: <PROJECT-HOME>/doc/bioplux/sensors/Electrocardiography_(ECG)_User_Manual.pdf
- [3] biosignalsplux `official ECG-sensor website <https://biosignalsplux.com/products/sensors/electrocardiography.html>`_

**Note**: there is **sample data** and **jupyter-notebooks** available in the **website's [3] Download section**.

---

ECG signal are comprised of multiple sources.
CG signal is comprised of multiple sources.
The recording is made through electrodes on the skin, which capture more than just the electrical activity of the heart.
The primary electrical components captured are the myocardium, muscle, skin-electrode interface, and external interference.

The common frequencies of the important components on the ECG:

- Heart rate: 0.67 – 5 Hz (i.e. 40 – 300 bpm)
- P-wave: 0.67 – 5 Hz
- QRS: 10 – 50 Hz
- T-wave: 1 – 7 Hz
- High frequency potentials: 100 – 500 Hz

The common frequencies of the artifact and noise on the ECG:

- Muscle: 5 – 50 Hz
- Respiratory: 0.12 – 0.5 Hz (e.g. 8 – 30 bpm)
- External electrical: 50 or 60 Hz (A/C mains or line frequency)
- Other electrical: typically >10 Hz (muscle stimulators, strong magnetic fields, pacemakers with impedance monitoring)

Filtering on an ECG is done four fold: high-pass, low-pass, notch, and common mode filtering.
- High-pass filters remove low frequency signals (i.e. only higher frequencies may pass), and
- low-pass filters remove high frequency signals.
  The high-pass and low-pass filters together are known as a bandpass filter,
  literally allowing only a certain frequency band to pass through.
- The notch filter is used to eliminate the line frequency and is usually printed on the ECG (e.g. ~60 Hz).
Common mode rejection is often done via right-leg drive, where an inverse signal of the three limb electrodes
are sent back through the right leg electrode.

Low-pass filters on the ECG are used to remove high frequency muscle artifact and external interference.
They typically attenuate only the amplitude of higher frequency ECG components.
Analog low-pass filtering has a noticeable affect on the QRS complex, epsilon, and J-waves
but do not alter repolarization signals.

High-pass filters remove low-frequency components such as motion artifact, respiratory variation, and baseline wander.
Unlike low-pass filters, analog high-pass filters do not attenuate much of the signal.
However, analog high-pass filters suffer from phase shift affecting the first 5 to 10 harmonics of the signal.
This means that a 0.5 Hz high pass filter, which is a lower frequency than the myocardium produces,
still can affect frequencies up to 5 Hz!

Source: [Fire EMS](http://ems12lead.com/2014/03/10/understanding-ecg-filtering/#gref)

---
"""

import numpy as np
import scipy as sp
import scipy.signal
from biofb.signal.filter import notch
from biofb.signal.filter import bandpass
from biofb.signal.detect import find_peaks
from biofb.signal.detect import check_peaks


def ecg_bandpass_filter(sampling_rate, notch_w0=(50., 60.), notch_Q=30., bandpass_N=10, bandpass_Wn=(0.05, 15), filtfilt=True):
    """ECG bandpass filter following the [Fire EMS](http://ems12lead.com/2014/03/10/understanding-ecg-filtering/#gref) blog.

    ---

    From the Blog:

    - Use a frequency setting appropriate for your equipment and clinical setting.
      Most 12-Lead ECG’s should be acquired at 0.05 – 150 Hz for full fidelity ST-segments and late potentials
      (such as epsilon or J-waves).
      **A decent compromise with 0.05 – 40 Hz or 0.05 – 100 Hz can be used if muscle artifact is severe**,
      provided you’re aware of the amplitude distortions which will occur.
    - Always read the frequency settings and calibration pulse when interpreting an ECG.
      These provide valuable information in order to accurately interpret the ECG!

    ---

    :param sampling_rate: sampling rate of the ECG data.
    :param notch_w0: Frequency (or list of frequencies) to be removed from a signal (via notch filter).
    :param notch_Q: Dimensionless quality factor that characterizes notch filter -3 dB bandwidth `bw` relative to its center frequency, `Q = w0/bw`.
    :param bandpass_N: The order of the filter (int, defaults to `5`).
    :param bandpass_Wn: Lower and Upper critical frequency or frequencies specifying the bandpass frequencies (array_like, defaults to `(0.05, 100)` Hz).
                        For digital units, `Wn` is the same units as `sampling_rate`.
    :param filtfilt: Boolean controlling whether `scipy.signal.filtfilt` or regular `scipy.signal.filt` methods are used (corrects phase-shift).
    :return: Callable bandpass filter which takes an array_like signal as input.
    """

    notch_filters = [
        notch(w0=w0, Q=notch_Q, sampling_rate=sampling_rate)
        for w0 in (notch_w0 if hasattr(notch_w0, '__iter__') else [notch_w0])
    ]

    bandpass_sos_filter = bandpass(N=bandpass_N, Wn=bandpass_Wn, sampling_rate=sampling_rate, analog=False)

    def apply_filter(x):
        for notch_filter in notch_filters:

            x = sp.signal.lfilter(*notch_filter, x) if not filtfilt else sp.signal.filtfilt(*notch_filter, x[::-1])[::-1]  # (b, a, x)

        x = sp.signal.sosfilt(bandpass_sos_filter, x) if not filtfilt else sp.signal.sosfiltfilt(bandpass_sos_filter, x[::-1])[::-1]
        return x

    return apply_filter


def find_R_peak_events(signal,
                       sampling_rate,
                       moving_window_integration_size=0.08,
                       R_peak_distinction_range=0.75,
                       R_peak_window_size=0.175,
                       ecg_filter=None):
    """Detect R peaks in ECG signal.

    Here we apply the Pan-Tompkins Algorithm []
    following the [tutorial](https://plux.info/signal-processing/461-event-detection-r-peaks-ecg.html)
    from *biosignalsplux* open source notebooks.

    :param signal: ECG signal array.
    :param sampling_rate: sampling rate of the ECG signal.
    :param moving_window_integration_size: Fraction of sampled data-points (given by sampling_rate)
                                           used in cummulative integration around mean point.
    :param ecg_filter: Custom ECG filter, defaults to `ecg_bandpass_filter`.
    :return: Numpy array, listing the indices of the estimated R peaks in the ECG signal array.
    :todo: The function needs to be refined for other test scenarios.
    """

    if ecg_filter is None or isinstance(ecg_filter, dict):
        ecg_filter = {} if ecg_filter is None else ecg_filter
        ecg_filter = ecg_bandpass_filter(sampling_rate=sampling_rate, **ecg_filter)

    # Step 1 of Pan-Tompkins Algorithm - ECG Filtering (Bandpass between 5 and 15 Hz)
    filtered_signal = ecg_filter(signal)

    # Step 2 of Pan-Tompkins Algorithm - ECG Differentiation
    differentiated_signal = np.diff(filtered_signal)

    # Step 3 of Pan-Tompkins Algorithm - ECG Rectification
    squared_signal = differentiated_signal * differentiated_signal

    # Step 4 of Pan-Tompkins Algorithm - ECG Integration ( Moving window integration )
    # - Definition of the samples number inside the moving average window
    n_win_smpl = int(moving_window_integration_size * sampling_rate)
    # - Initialisation of the variable that will contain the integrated signal samples
    integrated_signal = np.zeros_like(squared_signal)
    # - Determination of a cumulative version of "squared_signal"
    cumsum_signal = squared_signal.cumsum()

    # - Estimation of the area/integral below the curve that defines the "squared_signal"
    integrated_signal[n_win_smpl:] = (cumsum_signal[n_win_smpl:] - cumsum_signal[:-n_win_smpl]) / n_win_smpl
    integrated_signal[:n_win_smpl] = cumsum_signal[:n_win_smpl] / np.arange(1, n_win_smpl + 1)

    # Step 6: Detection of possible and probable R peaks
    # - find probable and possible peaks
    probable_peaks, possible_peaks = find_peaks(x=integrated_signal, distinction_range=R_peak_distinction_range)

    # - Identification of definitive R peaks
    R_peak_window = R_peak_window_size * sampling_rate
    definitive_peaks = check_peaks(x=integrated_signal, peaks=probable_peaks, peak_window=R_peak_window)

    # - Remap indices (see opensignalsplux notebooks)
    def map_integers(x):
        x = np.asarray(x)
        return x - 40 * (sampling_rate / 1000) - 1

    definitive_peaks_reph = np.array(list(map(int, map_integers(definitive_peaks))))

    return definitive_peaks_reph

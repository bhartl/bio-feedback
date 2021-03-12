from biofb.hardware import Channel
from biofb.signal.channels import ecg
import numpy as np


class ECG(Channel):
    """ **E**lectro **C**ardio **G**ram: Channel for Electrical Activity of the Heart.

        **Note**: AN ECG channel may be used by the **bioplux** hub
    """

    def __init__(self, *args, **kwargs):
        """

        :param args: Arguments forwarded to `Channel` constructor.
        :param kwargs: Keyword arguments forwarded to `Channel` constructor.
        """

        Channel.__init__(self, *args, **kwargs)

    def get_R_peaks(self, **kwargs):
        data = self.data
        return ecg.find_R_peak_events(data, sampling_rate=self.sampling_rate, **kwargs)

    def get_cardiogram(self, R_peaks=None, **kwargs):
        """ Time interval between R peak events in an ECG signal.

        :param R_peaks: Optional pre-evaluated R_peaks positions
                        (defaults to None -> `self.get_R_peaks(**kwargs)` is called).
        :param kwargs: Keyword-arguments to be forwarded to `get_R_peaks` method (only if `R_peaks` argument is None).
        :return: tachogram_time and tachogram_data
        """

        data = self.data
        time = self.time

        if R_peaks is None:
            R_peaks = self.get_R_peaks(**kwargs)

        time_r_peaks, amp_r_peaks = time[R_peaks], data[R_peaks]

        tachogram_data = np.diff(time_r_peaks)

        # The tachogram time can be obtained by
        # shifting each point of heartbeat duration
        # to the center of the two corresponding peaks.
        tachogram_time = (time_r_peaks[1:] + time_r_peaks[:-1]) / 2

        return tachogram_time, tachogram_data

    def get_heart_rate(self, bpm=True, R_peaks=None, **kwargs):
        """ Heart rate of current ECG data.

        :param bpm: Boolean controlling whether to show heart rate in **b**eats **p**er **m**inute (if True)
                    or per second (if False).
        :param R_peaks: Optional pre-evaluated R_peaks positions, forwarded to `get_cardiogram` along with `kwargs`.
        :param kwargs: Optional kwargs forwarded to `get_cardiogram` along with `R_peaks`.
        :return: tachogram_time and heart_rate
        """

        tachogram_time, tachogram_data = self.get_cardiogram(R_peaks=R_peaks, **kwargs)
        heart_rate_Hz = 1./tachogram_data

        return tachogram_time, (heart_rate_Hz * 60.) if bpm else (heart_rate_Hz)



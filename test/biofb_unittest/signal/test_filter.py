import unittest
import numpy as np
import scipy as sp
import scipy.signal


class TestSignalFiltering(unittest.TestCase):

    def setUp(self) -> None:

        self.T = 1
        self.sr = 1000
        self.duration = 1

        self.steps = np.arange(0, self.duration*self.sr)
        self.time = self.steps*self.T/self.sr
        self.frequencies = np.linspace(10, 20, 2)
        self.phase_shifts = np.random.rand(len(self.frequencies)) * 0.
        self.amplitudes = np.random.rand(len(self.frequencies)) * 0. + 1.

        self.phases = 2.*np.pi*(self.time[None, :]*self.frequencies[:, None] + self.phase_shifts[:, None])  # shape = (n_frequ x n_time)
        self.signals = self.amplitudes[:, None] * np.sin(self.phases)

        self.signal = np.sum(self.signals, axis=0)
        self.filtered = None

    def plot_signals(self):
        import matplotlib.pyplot as plt
        f, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True, sharey=True)
        [ax1.plot(self.time, s, label='{} Hz'.format(Hz))
         for s, Hz in zip(self.signals, self.frequencies)]

        ax2.plot(self.time, self.signal, label='signal')

        if self.filtered is not None:
            ax2.plot(self.time, self.filtered, label='filtered', color='tab:orange')

        ax1.set_ylabel('Amplitude')
        ax1.legend()

        ax2.set_xlabel('Time [s]')
        ax2.set_ylabel('Amplitude')
        ax2.legend()

        plt.show()

    def tearDown(self) -> None:
        pass

    def test_import(self, plot=False):

        if plot:
            self.plot_signals()

    def test_bandfilter(self, plot=False, N=10, Wn=15, filter='highpass', filtfilt=False):
        import biofb.signal.filter as preprocessing
        from biofb.signal.filter import apply_sos_filter

        bandfilter = getattr(preprocessing, filter)

        sos_filter = bandfilter(N=N, Wn=Wn, sampling_rate=self.sr, analog=False)
        if filtfilt:
            self.filtered = sp.signal.sosfiltfilt(sos_filter, self.signal)
        else:
            self.filtered = sp.signal.sosfilt(sos_filter, self.signal)

        if plot:
            self.plot_signals()

        filtered_1 = apply_sos_filter(self.signal, sos_filter=filter, N=N, Wn=Wn, sampling_rate=self.sr, analog=False, filtfilt=filtfilt)
        filtered_2, applied_sos_filter = apply_sos_filter(self.signal, sos_filter=filter, N=N, Wn=Wn, sampling_rate=self.sr, analog=False, return_filter=True, filtfilt=filtfilt)

        if filtfilt:
            refiltered_2 = sp.signal.sosfiltfilt(applied_sos_filter, self.signal)
        else:
            refiltered_2 = sp.signal.sosfilt(applied_sos_filter, self.signal)

        #self.assertTrue(np.array_equal(self.filtered, filtered_2))  # TODO
        #self.assertTrue(np.array_equal(filtered_1, filtered_2))
        #self.assertTrue(np.array_equal(filtered_2, refiltered_2))

    def test_lowpass(self, plot=False, N=10, Wn=15):
        return self.test_bandfilter(plot=plot, N=N, Wn=Wn, filter='lowpass')

    def test_bandpass_bandplot(self, plot=False, N=10, band_low=(5, 15), band_high=(15, 25)):
        self.test_bandfilter(plot=False, N=N, Wn=band_low, filter='bandpass', filtfilt=True)
        low_pass = np.array(self.filtered)

        self.test_bandfilter(plot=False, N=N, Wn=band_high, filter='bandstop', filtfilt=True)
        high_block = np.array(self.filtered)

        self.test_bandfilter(plot=False, N=N, Wn=band_high, filter='bandpass', filtfilt=True)
        low_block = np.array(self.filtered)

        self.test_bandfilter(plot=False, N=N, Wn=band_low, filter='bandstop', filtfilt=True)
        high_pass = np.array(self.filtered)

        N2 = len(self.time)//2

        low_diff = low_pass - high_block
        high_diff = low_block - high_pass

        self.assertTrue(np.max(np.absolute(low_diff[:N2])) < 0.25)
        self.assertTrue(np.max(np.absolute(high_diff[:N2])) < 0.25)

        if plot:
            import matplotlib.pyplot as plt

            f, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12), sharey=True, sharex=True)

            ax1.set_title('Filter High Frequencies.')
            ax1.plot(self.time, low_pass, label='low pass')
            ax1.plot(self.time, high_block, label='high stop')
            ax1.plot(self.time, low_diff, label='difference')

            ax2.set_title('Filter Low Frequencies.')
            ax2.plot(self.time, low_block, label='low stop')
            ax2.plot(self.time, high_pass, label='high pass')
            ax2.plot(self.time, high_diff, label='difference')

            ax1.legend()
            ax2.legend()

            plt.show()




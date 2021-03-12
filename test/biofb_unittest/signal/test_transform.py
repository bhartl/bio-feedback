import unittest
import numpy as np
import scipy as sp
import scipy.signal


class TestSignalTransformations(unittest.TestCase):

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

    def test_bandfilter_fourier_transform(self, plot=False, N=5, Wn=15, filter='highpass'):
        import biofb.signal.filter as preprocessing

        bandfilter = getattr(preprocessing, filter)

        sos_filter = bandfilter(N=N, Wn=Wn, sampling_rate=self.sr, analog=False)
        self.filtered = sp.signal.sosfilt(sos_filter, self.signal)

        from biofb.signal.transform import fast_fourier_transform
        xf_signal, yf_signal = fast_fourier_transform(self.signal, sampling_rate=self.sr, period=self.T, dB=True)
        xf_filtered, yf_filtered = fast_fourier_transform(self.filtered[300:], sampling_rate=self.sr, period=self.T, dB=True)
        xwf_filtered, ywf_filtered = fast_fourier_transform(self.filtered[300:], sampling_rate=self.sr, period=self.T, window=True, dB=True)

        if plot:
            import matplotlib.pyplot as plt
            plt.plot(xf_signal, yf_signal, label='signal')
            plt.plot(xf_filtered, yf_filtered, label='filtered')
            plt.plot(xwf_filtered, ywf_filtered, label='filtered with window')
            plt.ylabel('Amplitude [dB]')
            plt.show()

        #todo: actual test


if __name__ == '__main__':
    unittest.main()

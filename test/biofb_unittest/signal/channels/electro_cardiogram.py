import unittest
from biofb.hardware.devices import Bioplux


class TestSignalECG(unittest.TestCase):

    def setUp(self) -> None:
        fname = "data/session/sample/bioplux/opensignals_0007800f315c_2021-01-19_15-03-08_converted.txt"
        self.bp = Bioplux()
        self.bp.data = self.bp.load_data(filename=fname, update_device=True, update_channels=True)

        self.ecg_time = self.bp['ECG'].time
        self.ecg_data = self.bp['ECG'].data
        self.ecg_sampling_rate = self.bp['ECG'].sampling_rate
        self.ecg_data_R_peaks = [70,  409,  743, 1075, 1416, 1789, 2174, 2562, 2958, 3368, 3770, 4147]

    def tearDown(self) -> None:
        pass

    def test_import(self):
        pass

    def test_ecg_bandpass_filter(self, plot=False):

        from biofb.signal.channels.electro_cardiogram import ecg_bandpass_filter
        ecg_filter = ecg_bandpass_filter(sampling_rate=self.ecg_sampling_rate, filtfilt=True)
        filtered = ecg_filter(self.ecg_data)

        from biofb.signal.channels.electro_cardiogram import find_R_peak_events
        probable_peaks = find_R_peak_events(self.ecg_data, sampling_rate=self.ecg_sampling_rate)

        for prob_peak, det_peak  in zip(probable_peaks, self.ecg_data_R_peaks):
            self.assertTrue(prob_peak - 1 <= det_peak <= prob_peak + 1)

        if plot:
            import matplotlib.pyplot as plt

            plt.plot(self.ecg_time, self.ecg_data, label='ECG signal')
            plt.plot(self.ecg_time, filtered, label='filtered ECG')

            plt.scatter(self.ecg_time[probable_peaks], self.ecg_data[probable_peaks], label='probable peaks')
            plt.scatter(self.ecg_time[probable_peaks], filtered[probable_peaks], label='probable peaks (filtered ECG)')
            plt.legend()

            plt.xlabel('Time [s]')
            plt.ylabel('ECG [mV]')
            plt.show()


if __name__ == '__main__':
    unittest.main()

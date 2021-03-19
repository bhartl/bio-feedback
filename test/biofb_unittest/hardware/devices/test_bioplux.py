import unittest
from os import path


class TestBioplux(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_load_bioplux_data(self, plot=False):
        filename = "data/session/sample/bioplux/opensignals_0007800f315c_2021-01-19_15-03-08_converted.txt"
        filename = path.abspath(filename)

        from biofb.hardware.devices import Bioplux

        bioplux = Bioplux()
        data = bioplux.load_data(filename=filename, update_device=True, update_channels=True, update_sampling_rate=True)

        self.assertEqual(bioplux.name, "00:07:80:0F:31:5C")
        channel_names = ["DI", "EOG", "ECG", "RESPIRATION", "EEG", "EDA", "CUSTOM/0.5/1.0/V"]
        channel_labels = [bioplux.sensor_to_label(s) for s in channel_names]  # "DI", "CH1", "CH2", "CH3", "CH4", "CH5", "CH8"]
        for i, channel in enumerate(bioplux.channels):
            self.assertEqual(channel.sampling_rate, 500)
            self.assertEqual(channel.name, channel_names[i])
            self.assertEqual(channel.label, channel_labels[i])

        if plot:
            bioplux.plot(data=data.T, label_by='name', figure_kwargs={'figsize': (17, 10), 'sharex': True})

    def test_load_bioplux_db(self, plot=False):
        db_fname = "data/session/sample/bioplux/db-bioplux-01.yml"

        from biofb.io import SessionDatabase as Database
        from biofb.hardware.devices import Bioplux
        import numpy as np

        try:  # try execution from test directory
            db = Database.load(db_fname)
        except FileNotFoundError:
            db = Database.load(path.join('test', db_fname))

        for s in db.samples:
            self.assertIsInstance(s.setup.devices[0], Bioplux)
            self.assertIsInstance(s.setup['bioplux'], Bioplux)
            self.assertIs(s.setup['bioplux'], s.setup.devices[0])
            self.assertIs(s.setup, s.setup['bioplux']._setup)

        for s in db.samples:
            bp = s.setup.devices[0]
            self.assertIsInstance(bp, Bioplux)

            d = bp.data
            for i, c in enumerate(bp.channels):
                if plot:
                    print(f'channel {i}: {c}')
                self.assertTrue(np.array_equal(c.data, d[:, i]))

            if plot:
                bp.plot(figure_kwargs={'figsize': (17, 10), 'sharex': True})


if __name__ == '__main__':
    unittest.main()

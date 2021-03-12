import unittest
from os import path


class TestUnicorn(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_load_unicorn_data(self, plot=False):
        filename = "data/session/sample/unicorn/data-recorder/UnicornRecorder_20210125_144721.csv"

        from biofb.hardware.devices import Unicorn

        unicorn = Unicorn()

        try:  # try execution from test directory
            data = unicorn.load_data(filename=filename)
        except FileNotFoundError:
            data = unicorn.load_data(filename=path.join('test', filename))

        if plot:
            unicorn.plot(data=data.T, figure_kwargs={'figsize': (17, 10), 'sharex': True})

    def test_load_unicorn_db(self, plot=False):
        db_fname = "data/session/sample/unicorn/db-unicorn-01.yml"

        from biofb.io import SessionDatabase as Database
        from biofb.hardware.devices import Unicorn
        import numpy as np

        try:  # try execution from test directory
            db = Database.load(db_fname)
        except FileNotFoundError:
            db = Database.load(path.join('test', db_fname))

        for s in db.samples:
            self.assertIsInstance(s.setup.devices[0], Unicorn)
            self.assertIsInstance(s.setup['unicorn'], Unicorn)
            self.assertIs(s.setup['unicorn'], s.setup.devices[0])

        for s in db.samples:
            uc = s.setup.devices[0]
            self.assertIsInstance(uc, Unicorn)

            try:
                d = uc.data
            except (OSError, FileNotFoundError):
                s.filename = path.join('test', s.filename)
                d = uc.data

            for i, c in enumerate(uc.channels):
                if plot:
                    print(f'channel {i}: {c}')
                self.assertTrue(np.array_equal(c.data, d[:, i]))

            if plot:
                uc.plot(figure_kwargs={'figsize': (17, 10), 'sharex': True})


if __name__ == '__main__':
    unittest.main()

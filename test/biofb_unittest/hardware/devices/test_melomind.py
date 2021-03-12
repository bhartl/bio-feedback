import unittest
from os import path


class TestMelomind(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_load_melomind_data(self, plot=False):
        filename = "data/session/sample/melomind/output-202012181719.dat"
        filename = path.abspath(filename)

        from biofb.hardware.devices import Melomind

        melomind = Melomind()
        data = melomind.load_data(filename=filename)

        if plot:
            melomind.plot(data=data.T, figure_kwargs={'figsize': (17, 10), 'sharex': True})

    def test_load_unicorn_db(self, plot=False):
        db_fname = "data/session/sample/melomind/db-melomind-01.yml"

        from biofb.io import SessionDatabase as Database
        from biofb.hardware.devices import Melomind
        import numpy as np

        try:  # try execution from test directory
            db = Database.load(db_fname)
        except FileNotFoundError:
            db = Database.load(path.join('test', db_fname))

        for s in db.samples:
            self.assertIsInstance(s.setup.devices[0], Melomind)
            self.assertIsInstance(s.setup['melomind'], Melomind)
            self.assertIs(s.setup['melomind'], s.setup.devices[0])

        for s in db.samples:
            mm = s.setup.devices[0]
            self.assertIsInstance(mm, Melomind)

            d = mm.data
            for i, c in enumerate(mm.channels):
                self.assertTrue(np.array_equal(c.data, d[:, i]))

            if plot:
                mm.plot(figure_kwargs={'figsize': (17, 10), 'sharex': True})


if __name__ == '__main__':
    unittest.main()

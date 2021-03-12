import unittest
from os import path


class TestSessionDatabase(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_import(self):
        from biofb.io import SessionDatabase
        SessionDatabase()

    def test_load_db(self):
        from biofb.io import SessionDatabase
        from biofb.hardware import Device

        db_fname = 'data/session/sample/melomind/db-melomind-bare-device-01.yml'

        try:  # try execution from test directory
            db = SessionDatabase.load(db_fname)
        except FileNotFoundError:
            db = SessionDatabase.load(path.join('test', db_fname))

        for s in db.samples:
            mm = s.setup.devices[0]
            self.assertIsInstance(mm, Device)


if __name__ == '__main__':
    unittest.main()

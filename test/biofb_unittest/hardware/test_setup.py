import unittest


class TestSetup(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_import(self):
        from biofb.hardware import Setup


if __name__ == '__main__':
    unittest.main()

import unittest


class TestSample(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_import(self):
        from biofb.session import Sample

    def test_construct(self):
        from biofb.session import Sample


if __name__ == '__main__':
    unittest.main()

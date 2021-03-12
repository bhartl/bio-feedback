import unittest


class TestLocation(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_import(self):
        from biofb.session import Location

    def test_construct(self):
        from biofb.session import Location

        subject = Location(name='Test Location', comment="Test Comment on Location.")
        self.assertEqual(subject.name, 'Test Location')
        self.assertEqual(subject.comment, "Test Comment on Location.")

    def test_load(self):
        from biofb.session import Location

        subject = Location.load(dict(name='Loaded Location', comment='Loaded from Dict.'))
        self.assertEqual(subject.name, "Loaded Location")
        self.assertEqual(subject.comment, "Loaded from Dict.")


if __name__ == '__main__':
    unittest.main()

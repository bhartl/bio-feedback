import unittest


class TestSubject(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_import(self):
        from biofb.session import Subject

    def test_construct(self):
        from biofb.session import Subject

        subject = Subject(identity='Test Subject', comment="Test Comment on Subject.")

        with self.assertRaises(AssertionError):
            subject.name

        with self.assertRaises(AssertionError):
            subject.initials

        self.assertEqual(subject.comment, "Test Comment on Subject.")

    def test_load(self):
        from biofb.session import Subject

        subject = Subject.load(dict(identity='Loaded Subject', comment='Loaded from Dict.'))
        self.assertEqual(subject.identity, "Loaded Subject")
        self.assertEqual(subject.comment, "Loaded from Dict.")


if __name__ == '__main__':
    unittest.main()

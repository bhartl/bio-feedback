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

    def test_privacy_create_file(self, id_file='data.local/privacy_test/id_file.csv'):
        from biofb.session import Subject
        import pandas as pd

        def query_id_file(df, identity, name, given_name):
            if isinstance(df, str):
                df = pd.read_csv(df)

            assert isinstance(df, pd.DataFrame)

            df_id = df[df.ID == identity]
            assert len(df_id) == 1
            assert all(df_id['Given Name'] == given_name)
            assert all(df_id['Name'] == name)

            return df

        # crate subject with name
        s1 = Subject(identity=123456, id_file=id_file, name="Test Subject")
        s2 = Subject(identity=123457, id_file=id_file, name=["Test 2", "Subject 2"])
        s3 = Subject(identity=123458, id_file=id_file, name={"First Name": "Test 3", "Name": "Subject 3"})

        id_df = query_id_file(df=id_file, identity=s1.identity, name='Subject', given_name='Test')
        id_df = query_id_file(df=id_file, identity=s2.identity, name='Subject 2', given_name='Test 2')
        id_df = query_id_file(df=id_file, identity=s3.identity, name='Subject 3', given_name='Test 3')

        # check whether name is protected
        with self.assertRaises(AssertionError):
            print(s1.name)

        s1.respect_privacy = False
        self.assertEqual(s1.name, "Test Subject")

        # rename -> changes identity entry in id-file
        s1.name = "Firstname Surname"
        self.assertEqual(s1.name, "Firstname Surname")
        s1.respect_privacy = True

        # check whether name is protected
        with self.assertRaises(AssertionError):
            print(s1.name)

        # query previously loaded id file (not updated)
        query_id_file(df=id_df, identity=s1.identity, name='Subject', given_name='Test')

        # query current id-file with changed name (updated by rename)
        with self.assertRaises(AssertionError):
            query_id_file(df=id_file, identity=s1.identity, name='Subject', given_name='Test')
        query_id_file(df=id_file, identity=s1.identity, name='Surname', given_name='Firstname')
        query_id_file(df=id_file, identity=s2.identity, name='Subject 2', given_name='Test 2')
        query_id_file(df=id_file, identity=s3.identity, name='Subject 3', given_name='Test 3')

        s1.name = ("Firstname 2", "Surname 2")
        query_id_file(df=id_file, identity=s1.identity, name='Surname 2', given_name='Firstname 2')
        query_id_file(df=id_file, identity=s2.identity, name='Subject 2', given_name='Test 2')
        query_id_file(df=id_file, identity=s3.identity, name='Subject 3', given_name='Test 3')

        s2.name = ("Firstname 3", "Surname 3")
        query_id_file(df=id_file, identity=s1.identity, name='Surname 2', given_name='Firstname 2')
        query_id_file(df=id_file, identity=s2.identity, name='Surname 3', given_name='Firstname 3')
        query_id_file(df=id_file, identity=s3.identity, name='Subject 3', given_name='Test 3')

        s3.name = {"Given Name": "Firstname 4", "Surname": "Surname 4"}
        query_id_file(df=id_file, identity=s1.identity, name='Surname 2', given_name='Firstname 2')
        query_id_file(df=id_file, identity=s2.identity, name='Surname 3', given_name='Firstname 3')
        query_id_file(df=id_file, identity=s3.identity, name='Surname 4', given_name='Firstname 4')


if __name__ == '__main__':
    unittest.main()

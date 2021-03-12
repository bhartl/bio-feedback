import unittest
import os.path as path


class TestLoadable(unittest.TestCase):

    def setUp(self) -> None:
        self.data_path = 'data/io/test_load_dict_like.local/'

    def tearDown(self) -> None:
        pass

    def test_import(self):
        from biofb.io import Loadable

    def test_load_dict_like_yaml(self):
        from biofb.io import Loadable
        import yaml
        import os

        dict_obj = dict(test=1, abc="str")

        # check identity
        self.assertIs(Loadable.load_dict_like(value=dict_obj), dict_obj)

        # check yaml load
        yaml_repr = yaml.safe_dump(dict_obj)
        loaded = Loadable.load_dict_like(value=yaml_repr)
        self.assertIsInstance(loaded, dict)
        self.assertEqual(loaded, dict_obj)
        loaded['test'] = 2
        self.assertNotEqual(loaded, dict_obj)

        # check file-load
        path = self.data_path
        if not os.path.exists(path):
            os.makedirs(path)

        yml_file = os.path.join(path, 'dict-repr.yml')
        with open(yml_file, 'w') as s:
            s.write(yaml_repr)
        loaded = Loadable.load_dict_like(value=yml_file)
        self.assertIsInstance(loaded, dict)
        self.assertEqual(loaded, dict_obj)
        loaded['test'] = 2
        self.assertNotEqual(loaded, dict_obj)

    def test_load_dict_like_json(self):
        from biofb.io import Loadable
        import json
        import os

        dict_obj = dict(test=1, abc="str")

        # check identity
        self.assertIs(Loadable.load_dict_like(value=dict_obj), dict_obj)

        # check json load
        json_repr = json.dumps(dict_obj)
        loaded = Loadable.load_dict_like(value=json_repr)
        self.assertIsInstance(loaded, dict)
        self.assertEqual(loaded, dict_obj)
        loaded['test'] = 2
        self.assertNotEqual(loaded, dict_obj)

        # check file-load
        path = self.data_path
        if not os.path.exists(path):
            os.makedirs(path)

        json_file = os.path.join(path, 'dict-repr.json')
        with open(json_file, 'w') as s:
            s.write(json_repr)
        loaded = Loadable.load_dict_like(value=json_file)
        self.assertIsInstance(loaded, dict)
        self.assertEqual(loaded, dict_obj)
        loaded['test'] = 2
        self.assertNotEqual(loaded, dict_obj)

    def test_load_dict_like_repr(self):
        from biofb.io import Loadable

        dict_obj = dict(test=1, abc="str")

        # check identity
        self.assertIs(Loadable.load_dict_like(value=dict_obj), dict_obj)

        # check repr load
        dict_repr = repr(dict_obj)
        loaded = Loadable.load_dict_like(value=dict_repr)
        self.assertIsInstance(loaded, dict)
        self.assertEqual(loaded, dict_obj)
        loaded['test'] = 2
        self.assertNotEqual(loaded, dict_obj)

    def test_load_dict_like_tuple(self):
        from biofb.io import Loadable

        dict_tuple = (('test', 1), ('abc', "str"))
        dict_obj = dict(dict_tuple)

        # check repr load
        loaded = Loadable.load_dict_like(value=dict_tuple)
        self.assertIsInstance(loaded, dict)
        self.assertEqual(loaded, dict_obj)
        loaded['test'] = 2
        self.assertNotEqual(loaded, dict_obj)

    def test_load_dict_like_assertion_errors(self):
        from biofb.io import Loadable

        dict_tuple = (('test', 1), ('abc', "str"), (3, ))

        with self.assertRaises(AssertionError):
            Loadable.load_dict_like(value=dict_tuple)

        with self.assertRaises(AssertionError):
            dict_obj = dict(dict_tuple[:2])
            dict_repr = repr(dict_obj)

            Loadable.load_dict_like(value=dict_repr[:-2])

        with self.assertRaises(AssertionError):
            Loadable.load_dict_like(value="test 1234")

        with self.assertRaises(AssertionError):
            Loadable.load_dict_like(value=path.join(self.data_path, "not-a-file-for-sure/do-not-create-this-path.yml"))

        with self.assertRaises(AssertionError):
            Loadable.load_dict_like(value=path.join(self.data_path, "not-a-file-for-sure/do-not-create-this-path.json"))


if __name__ == '__main__':
    unittest.main()

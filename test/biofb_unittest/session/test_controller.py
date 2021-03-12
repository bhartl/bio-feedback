import unittest


class TestController(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_import(self):
        from biofb.session import Controller

    def test_construct(self):
        from biofb.session import Controller

        controller = Controller(name='Test Controller', description="Test Comment on Controller.")
        self.assertEqual(controller.name, 'Test Controller')
        self.assertEqual(controller.description, "Test Comment on Controller.")

    def test_load(self):
        from biofb.session import Controller

        controller = Controller.load(dict(name='Loaded Controller', description='Loaded from Dict.'))
        self.assertEqual(controller.name, "Loaded Controller")
        self.assertEqual(controller.description, "Loaded from Dict.")

        controller = Controller.load(repr(dict(name='Loaded Controller', description='Loaded from Dict.')))
        self.assertEqual(controller.name, "Loaded Controller")
        self.assertEqual(controller.description, "Loaded from Dict.")


if __name__ == '__main__':
    unittest.main()

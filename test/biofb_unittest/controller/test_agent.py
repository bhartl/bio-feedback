import unittest


class TestAgent(unittest.TestCase):

    def setUp(self) -> None:
        from biofb.controller import Agent

        # overwrite abstract method `action`
        class TAgent(Agent):
            def __init__(self, *args, **kwargs):
                Agent.__init__(self, *args, **kwargs)

            def action(self, state):
                return

        self.TestAgent = TAgent

    def tearDown(self) -> None:
        pass

    def test_import(self):
        from biofb.controller import Agent

        # abstract method `action` needs to be specified:
        with self.assertRaises(NotImplementedError):
            agent = Agent()
            agent.action(state=None)

    def test_construct(self):
        agent = self.TestAgent(name='Test Agent', description="Test Description on Agent.")
        self.assertEqual(agent.name, 'Test Agent')
        self.assertEqual(agent.description, "Test Description on Agent.")

    def test_load(self):
        agent = self.TestAgent.load(dict(name='Loaded Agent', description='Loaded from Dict.'))
        self.assertEqual(agent.name, "Loaded Agent")
        self.assertEqual(agent.description, "Loaded from Dict.")


if __name__ == '__main__':
    unittest.main()

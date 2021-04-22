import unittest
import numpy as np


class TestSession(unittest.TestCase):

    def setUp(self) -> None:
        from biofb.controller import Session
        from biofb.controller import Agent
        from biofb.session import Sample

        class TSample(Sample):
            """ Test Sample whose state is an integer number, `i` """
            def __init__(self, i=0, imax=10):
                self.i = 0
                self.imax = imax

            @property
            def state(self):
                return self.i

        class TAgent(Agent):
            """ Test Agent whose action is an integer increment `inc` but randomly positive or negative"""
            def __init__(self, inc=1):
                self.inc = inc

            def action(self, state):
                dummy_state_dependent_sign = np.sign(np.random.rand() - 0.5/(state*0.1 + 1))
                return self.inc * dummy_state_dependent_sign

            def get_action(self, state):
                return self.action(state)

        # overwrite abstract method `step`
        class TSession(Session):
            """ Test Session whose step is to increase the state of its Test Sample using the Test Agent """

            def __init__(self, *args, agent=TAgent(), sample=TSample(), **kwargs):
                Session.__init__(self, *args, agent=agent, sample=sample, **kwargs)
                self.n_steps = 0

            def step(self, action):
                """ The step consists of

                - increasing the state of the sample ONLY, but if the action is positive
                - reading the new state
                - checking, whether the imax condition is satisfied (done or not)
                """
                self.sample.i += max([0, action])

                state = self.sample.state
                done = state >= self.sample.imax

                self.n_steps += 1

                return done, state, dict()

        self.TestSession = TSession
        self.TestAgent = TAgent
        self.TestSample = TSample

    def tearDown(self) -> None:
        pass

    def test_import(self):
        from biofb.controller import Session

        # abstract method `step` needs to be specified:
        with self.assertRaises(TypeError):
            Session(agent=None, sample=None)

    def test_construct(self):
        session = self.TestSession(name='Test Session', description="Test Description on Session.")
        self.assertEqual(session.name, 'Test Session')
        self.assertEqual(session.description, "Test Description on Session.")

    def test_load(self):
        subject = self.TestSession.load(dict(name='Loaded Session', description='Loaded from Dict.'))
        self.assertEqual(subject.name, "Loaded Session")
        self.assertEqual(subject.description, "Loaded from Dict.")

    def test_run_feedback_blocking(self, imax=10, iinc=1, i0=0):
        """ run controller loop as blocking loop (no threading) on TestSession environment (cf. setUp)"""

        session = self.TestSession(
            name='Test Session',
            description='Loaded from Dict.',
            agent=self.TestAgent(inc=iinc),
            sample=self.TestSample(i=i0, imax=imax),
        )

        self.assertEqual(session.n_steps, 0)
        session.run()

        self.assertTrue(session.done)
        self.assertTrue(session.sample.state >= imax)


if __name__ == '__main__':
    unittest.main()

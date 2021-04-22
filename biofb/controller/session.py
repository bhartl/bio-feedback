from biofb.io import Loadable
from biofb.session import Sample
from biofb.controller import Agent
from numpy import ndarray
import threading
from time import sleep
import os
from pydoc import locate


class Session(Loadable):
    """ Controller Session: `Agent` interacting with a `Subject`'s `Sample` state.

     Abstract ABCMeta class: `step` method (defining how the `Agent`'s action is
     applied and how the `Sample`'s state is captured) needs to be specified.

    Given the `state` of a measurement `Sample` (bio-signals) the `Controller`
    proposes an `action` (according to its internal policy) to guide the `state`
    towards a desired outcome.
    """

    SAMPLE_DATA_KEY = 'sample_data'
    ACTION_DATA_KEY = 'action_data'

    def __init__(self,
                 sample: Sample,
                 agent: Agent,
                 name: (str, None) = "Feedback Session",
                 description: str = "",
                 delay: float = 0.,
                 timeout: float = 2.,
                 sample_data=None,
                 action_data=None,
                 ):
        """Constructor of Feedback `Session`

        :param name: A Feedback `Session`'s name (str).
        :param sample: A `Sample` session object which is to be controlled.
        :param agent: An `Agent` object which controls a `Sample` data during a Feedback `Session`.
        :param description: Comment about the session (str, defaults to "").
        :param delay: Delay between controller-loop cycle steps.
        :param timeout: Timeout for stopping controller-loop (if started as background thread).
        :param sample_data: (Optional) Sample-data list which initializes the `data`-property of the sample instance,
                            e.g. when loading from a file (defaults to None).
        :param action_data: (Optional) Agent-data list which initializes the `action_data`-property of the agent
                            instance, e.g. when loading from a file (defaults to None).
        """

        Loadable.__init__(self)

        self._name = None
        self.name = name

        self._description = None
        self.description = description

        # load sample
        self._sample = None
        self.sample = sample

        if sample_data is not None:
            self.sample.data = sample_data

        # load agent
        self._agent = None
        self.agent = agent

        if action_data is not None:
            self.agent.action_data = action_data

        self._done = False
        self.done = False

        self._delay = None
        self.delay = delay

        self._timeout = None
        self.timeout = timeout

        self._feedback_loop_daemon = None

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: (str, None)):
        self._name = value if value is not None else "Session"

    @property
    def sample(self) -> Sample:
        return self._sample

    @sample.setter
    def sample(self, value: Sample):
        self._sample = Sample.load(value)

    @property
    def agent(self) -> Agent:
        return self._agent

    @agent.setter
    def agent(self, value: Agent):
        from biofb.session import Controller
        self._agent = Controller.load(value)

    @property
    def done(self) -> bool:
        return self._done

    @done.setter
    def done(self, value: bool):
        self._done = value

    @property
    def running(self) -> bool:
        if self._feedback_loop_daemon is None:
            return False

        return self._feedback_loop_daemon.run()

    @property
    def delay(self) -> float:
        return self._delay

    @delay.setter
    def delay(self, value: float):
        assert value >= 0
        self._delay = value

    @property
    def timeout(self) -> int:
        return self._timeout

    @timeout.setter
    def timeout(self, value: int):
        assert value >= 0
        self._timeout = value

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

    def __str__(self):
        return f"<Session: {self.name}>"

    def step(self, action: (ndarray, tuple, object)) -> tuple:
        """ Apply `Controller` `action` to subject and get `Sample` response (next `state`)

        :param action: Proposed action by the `Controller` instance, to be applied to the subject.
        :return: Tuple of (done, state, info-dict()), i.e.,
                 if session is done,
                 `Sample`-state of the subject and
                 an info-dictionary about the current state (optional, defaults to None).
        """
        raise NotImplementedError(f'{self.get_module_name()}.{self.get_class_name()}.step')

    def run(self, data_monitor=None) -> None:
        """ Controller main loop.

        - Actions are proposed according to the current state of the subject's acquired `sample`s.
        - The state of the subject is updated by the `agent`'s `action`s.
        - The goal is to guide the subject's state to exhibit certain qualities.

        :return: None
        """

        self.done = False          # start the agent loop (this could be done in an extra thread)

        state = self.sample.state  # acquire the initial state
        done = False

        while not done:
            action = self.agent.get_action(state)       # get action from agent instance and track action data
            done, state, info_dict = self.step(action)  # update sample state based on agent action

            try:
                data_monitor.data = [d.T for d in self.sample.data]
            except:
                pass

            if self.delay != 0.:
                sleep(self.delay)

        self.done = done
        return

    def start(self, **threading_kwargs) -> threading.Thread:
        """  Start the controller-loop cycle as independent thread.

        :param threading_kwargs: Keyword arguments to be forwarded to "threading.Thread" of the `feedback_loop` method.
        :todo: Test
        """

        assert not self.running, "No other feedback_loop session must be running."

        self._feedback_loop_daemon = threading.Thread(name='session-controller-loop',
                                                      target=self.run,
                                                      **threading_kwargs)
        self._feedback_loop_daemon.start()

        return self._feedback_loop_daemon

    def stop(self) -> None:
        """ Stop controller-loop cycle if it was started as independent thread (using the `start` method).

        :todo: Test
        """

        try:
            # stop data acquisition
            self.sample.setup.stop()
        except:
            pass

        if not self.running:
            return

        try:
            self._feedback_loop_daemon.terminate()
            self._feedback_loop_daemon.join(self.timeout)
            self._feedback_loop_daemon = None
        except:
            pass

        return

    def to_dict(self):
        dict_repr = super().to_dict()
        dict_repr['class'] = '.'.join([self.get_module_name(), self.get_class_name()])
        return dict_repr

    @classmethod
    def load(cls, value):

        if not isinstance(value, (dict, cls)):
            value = cls.load_dict_like(value)
            return cls.load(value)

        if isinstance(value, dict):

            try:
                session_cls = value.pop('class')
                session_cls = locate(session_cls)
            except KeyError:
                session_cls = cls

            if session_cls is not cls:
                return session_cls.load(value)

            return cls(**value)

        return super().load(value)

    def dump(self, filename=None, file_format=None, exist_ok=True):
        if filename is None:
            filename = self.sample.filename
            base, extension = os.path.splitext(filename)
            if extension.lower() not in ('.h5', '.hdf5', '.h5py'):
                filename = base + '.yml'

        if file_format is None:
            __, extension = os.path.splitext(filename)
            if extension.lower() in ('.h5', '.hdf5', '.h5py'):
                file_format = 'h5'
            elif extension.lower() in ('.json'):
                file_format = 'json'
            else:
                file_format = 'yml'

        super().dump(filename=filename, file_format=file_format, exist_ok=exist_ok)
        self.sample.dump_data(mode='a', key=self.SAMPLE_DATA_KEY)
        self.agent.dump_actions(filename=self.sample.filename, mode='a', key=self.ACTION_DATA_KEY)


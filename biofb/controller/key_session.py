from biofb.session import Sample
from biofb.controller import Session
from biofb.controller import KeyAgent
from numpy import ndarray


class KeySession(Session):
    """ A simple key-stroke controlled session:
    Recorded audio samples are mapped to key-strokes and replayed if latter are pressed.

    Bio-Data are captured and can be correlated with the specific audio data that has been played during the session.
    """

    def __init__(self,
                 sample: Sample,
                 agent: KeyAgent,
                 action_map: (dict, None) = None,
                 action_successive: bool = True,
                 name: (str, None) = "KeySession",
                 description: str = "",
                 delay: float = 1e-3,
                 timeout: float = 2.0,
                 convert_on_wave_error=True,
                 **replay_kwargs
                 ):
        """

        :param sample: The `Sample` object to acquire `Subject's `state` from.
        :param agent: The `Agent` used to propose `action`s on the `Sample`.
        :param action_map: Dict-like map of `actions` to audio output (`numpy arrays` or wav file names).
                           Optional (defaults to None): falls back to possible `agent.action_map`.
        :param action_successive: Boolean controlling whether actions are successive
                                  (can not be interrupted by next action, default True)
                                  or if new actions overwrite older ones.
        :param name: Name of the `KeySession`.
        :param description: Informal description of the `KeySession`.
        :param delay: Delay between action-step-state controller loop of the session.
        :param timeout: Timeout until terminate command is executed to terminate a session controller loop.
        :param convert_on_wave_error: Recordings might be in the wrong format,
                                      the corresponding files will be reformatted if True,
                                      Exceptions will be raised otherwise.
        :param replay_kwargs: Possible keyword arguments to be forwarded to `sa.play_buffer`, such as `sample_rate`.
        """

        Session.__init__(self, sample=sample, agent=agent, name=name,
                         description=description, delay=delay, timeout=timeout)

        assert isinstance(self.agent, KeyAgent)

        self._action_map = None
        self.action_map = action_map

        self._replay_kwargs = replay_kwargs
        self._replay = None
        self._action_successive = action_successive
        self._convert_on_wave_error = convert_on_wave_error

    @property
    def action_map(self):
        if self._action_map in (None, dict()):
            return self.agent.action_map

        return self._action_map

    @action_map.setter
    def action_map(self, value: (str, dict, None)):
        action_map = self.load_dict_like(value)
        self._action_map = action_map

    def step(self, action: (ndarray, tuple, object)) -> tuple:
        """ Replay (recorded) audio-controller via speaker, mapped via `action`.

        If the object is instanciated with `action_successive == True`, actions are only applied
        if no controller output is currently replayed (actions can not be truncated).

        :param action: Actions mapped to audio-data or path to controller data (to be replayed).
        :return: Tuple of (done, state, info-dict()) specifying
                 if the session is done (the session terminates on the condition `action is None`),
                 `Sample`-state of the subject and
                 an info-dictionary about the current state (optional, defaults to None).
        """

        done = action is None

        if not done:
            self.apply(action=action)

        state = self.sample.state
        info = dict()

        return done, state, info

    def apply(self, action) -> object:
        """ Replay controller data or controller file

        :param action: Suggested `action` by `Agent`,
                       to be mapped to controller audio data or file via the `action_map`.
        :returns: `simpleaudio.PlayObject` or None if action can not be interpreted
                  (or is not allowed to the `action_successive` specification).
        """
        if action in (None, "", (), {}):
            return

        key, action_map = action

        if key is None and action_map is None:  # check, if new action is proactive
            return

        assert key is not None

        try:
            to_apply = self.action_map[action_map]
            if hasattr(to_apply, '__call__'):
                return to_apply()

            else:
                return eval(to_apply)

        except Exception as ex:
            raise ex

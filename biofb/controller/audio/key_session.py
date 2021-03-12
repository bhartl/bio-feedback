from biofb.session import Sample
from biofb.controller.audio import KeyAgent
from biofb.controller import Session
from numpy import ndarray, shape
import simpleaudio as sa
from biofb.io import wave_file
from os.path import abspath


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

    @property
    def replaying(self) -> bool:
        """ Checks, whether the current replay object is currently playing.

        :return: `True`, if the current replay object is currently playing, `False` otherwise.
        """
        if self._replay is None:
            return False

        return self._replay.is_playing()

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
            self.replay(action=action)

        state = self.sample.state
        info = dict()

        return done, state, info

    def replay(self, action) -> (sa.PlayObject, None):
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

        if self.replaying:
            if self._action_successive:  # resume if new action must not overwrites old action
                return

            if action_map is None:  # check if cancel key was pressed
                self._replay.stop()
                return

        try:
            audio = self.action_map[action_map]

            if isinstance(audio, str):
                try:
                    audio_obj = sa.WaveObject.from_wave_file(abspath(audio))
                    self._replay = audio_obj.play()
                except Exception as ex:

                    # audio file can have unrecognizable format
                    if not self._convert_on_wave_error:
                        print(f'ERROR: An exception occurred: {type(ex)} {ex}')
                        print(wave_file.available_formats())
                        return None

                    # transform audio-format and relabel action_map
                    new_wav_file = wave_file.transform_format(audio, '.wav', '-converted.wav')
                    self.action_map[action_map] = new_wav_file

                    return self.replay(action)

            else:
                self._replay = sa.play_buffer(audio, min([shape(audio)[0], 1]), 2, **self._replay_kwargs)

        except Exception as ex:
            raise ex

        return self._replay

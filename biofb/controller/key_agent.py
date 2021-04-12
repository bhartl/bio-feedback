import threading
from numpy import ndarray
from pynput.keyboard import Key, Listener
from biofb.controller import Agent


class KeyAgent(Agent):
    """ Key `Agent` which action data from a database of recorded phrases by `Thomas Hill`
    (or other controller data).

    The selection of the controller data is performed manually via key-strokes
    that are mapped to every individual phrase via a configuration file.

    The `Subject`'s `Sample` state is not used by the `KeyAgent` `Agent`'s
    policy directly but by an external human controller.
    """

    def __init__(self,
                 name: (str, None) = "KeyAgent",
                 description: str = "",
                 keymap_action: (str, dict, None) = None,
                 action_map: (str, dict, None) = None,
                 sleep: (float) = 1e-3,
                 verbose: (bool) = True
                 ):
        """ Construct a `KeyAgent` instance.

        :param name: Name of the Agent.
        :param description: Informal description of the Agent.
        :param keymap_action: Key map to controller action (str or dict, defaults to None).
                        Can be a `dict` mapping keys to controller file `{key_1: audio_key_1, ...}`,
                        can be a path (`str`) to a loadable file (`dict/yml`) or
                        `None` (default option) which induces an alphabetic ordering
                        `{'a': audio_key_1, 'b': audio_key_1, ...}`.
        :param sleep: Time during consecutive keystroke detections
        :param verbose: Boolean controlling whether print notifications will be performed.
        """

        Agent.__init__(self, name=name, description=description)

        self._keymap_action = None
        self.keymap_action = keymap_action

        self._action_map = None
        self.action_map = action_map

        self._terminated = False

        self._detecting_keystrokes = None
        self._keyboard_listener = None
        self._sleep = sleep
        self._pressed_key = None
        self.set_pressed_key(0)

        self._keymap_terminate = Key.esc
        self._keymap_cancel_action = '.'
        self.verbose = verbose

    def __del__(self):
        self.terminate()

    def __str__(self):
        keystroke_str = [f'KeyAgent `{self.name}`: {self.description}']
        keystroke_str += [f'Keys to action map:']
        keystroke_str += [f'\t{k}:\t{f}' for k, f in self._keymap_action.items()]

        keystroke_str += [f'(Stop replay with \'{self._keymap_cancel_action}\', '
                          f'Stop Agent with \'{self._keymap_terminate}\')']


        longest = max([len(s) for s in keystroke_str])
        keystroke_str = ['-'*longest] + keystroke_str + ['-'*longest]

        return '\n'.join(keystroke_str)

    @property
    def keymap_action(self):
        return self._keymap_action

    @keymap_action.setter
    def keymap_action(self, value: (str, dict, None)):
        keymap = self.load_dict_like(value)
        self._keymap_action = keymap

    @property
    def action_map(self):
        return self._action_map

    @action_map.setter
    def action_map(self, value: (str, dict, None)):
        action_map = self.load_dict_like(value)
        self._action_map = action_map

    def action(self, state: (dict, ndarray)) -> (ndarray, str, None):
        """ Proposed `action` of the `KeyAgent`: Prerecorded controller data are selected via mapped key-strokes.

        :param state: Dictionary or array_like state of the subject (i.e., bio-signals)
                      which are acquired with bio-sensory devices.
        :return: Prerecorded controller data, selected via key-strokes according to the `KeyAgent`'s configuration.
        """

        if not self._detecting_keystrokes:
            self._detecting_keystrokes = threading.Thread(name='detect-keystrokes', target=self.detect_keystroke, daemon=True)
            self._detecting_keystrokes.start()
            if self.verbose: print('Press a `Key` from the specified `Keys-to-action map`.')

        key = self.pop_keystroke()

        if self.is_terminal(key):
            self.terminate()

        if self.terminated:
            return None

        if self.is_cancel(key):
            return key, None

        if key in self._keymap_action:
            return key, self._keymap_action[key]

        return ()

    def detect_keystroke(self) -> None:
        """ Starts a `on_press` / `on_release` `pynpt.Listener` for keyboard events. """
        with Listener(on_press=self.on_press, on_release=self.on_release) as self._keyboard_listener:
            self._keyboard_listener.join()

    def on_press(self, key):
        """ Listener method for key-press events.

        :param key: String representation of pressed key.
        """

        self.set_pressed_key(key)

    def on_release(self, key):
        """ Listener method for key-felease events.

        :param key: pynpt.Key instance representing the pressed key.
        :return: True per default, False if `ESC` key has been pressed (which stops the Listener).
        """
        return not self.is_terminal(key)

    def pop_keystroke(self):
        """ Pop/get possible pressed key event (performed by listener in independent thread).

         :returns: Character representation of pressed key.
         """
        # make thread-safe: self._pressed_key can be modified by on_press event

        pressed_key = self.get_pressed_key()

        if isinstance(pressed_key, list):
            # for test reasons, also a list of key-strokes is defined
            # this should ned be happening in productive applications
            try:
                key = pressed_key.pop(0)
            except IndexError:
                key = 0

        elif isinstance(pressed_key, int):
            # if pressed key is an integer, try to convert it to character
            key = chr(pressed_key)
            self.set_pressed_key(None)

        elif self.get_pressed_key() is None:
            key = None

        else:
            # the str representation of pynpt.Key is "\'{key}\'",
            # we remove the single-quote characters

            key = None

            if isinstance(pressed_key, str):
                key = pressed_key

                if len(key) > 1 and key.startswith("\'"):
                    key = key[1:]

                if len(key) > 1 and key.endswith("\'"):
                    key = key[:-1]
            else:
                print(pressed_key)

            self.set_pressed_key(None)

        return key

    def get_pressed_key(self):

        if self.terminated:
            return None

        return self._pressed_key

    def set_pressed_key(self, key):

        if not self.terminated:
            self._pressed_key = str(key) if key is not None else 0

    @property
    def terminated(self):
        return self._terminated

    def terminate(self, value=True):

        if not value:
            return False

        if self.terminated:
            return True

        try:
            self._keyboard_listener.stop()
        except AttributeError as ex:
            pass

        self._terminated = True
        self._detecting_keystrokes.join(self._sleep * 2)
        self._detecting_keystrokes = None
        return True

    def is_terminal(self, key):
        """ Checks, whether the specified key is equal to the terminal key `ESC`.

        :returns: True if key is not terminal key, False otherwise
        """

        if key is None:
            return False

        return str(key) == str(self._keymap_terminate)

    def is_cancel(self, key):
        """ Checks, whether the specified key is equal to the cancel key `<ctrl>-<c>`.

        :returns: True if key is cancel key, False otherwise
        """

        return str(key) == str(self._keymap_cancel_action)
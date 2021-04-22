from numpy import ndarray, nan
from biofb.session import Controller
from time import time
import os
import h5py


class Agent(Controller):
    """ Pro-active `Controller`-`Agent` of a controller session `Sample`.

     Abstract ABCMeta class: `action` method needs to be specified.

    Given the `state` of a measurement sample (bio-signals) the `Controller`-`Agent`
    proposes an `action` (according to its internal policy) based on the `Sample`'s `state`
    to achieve a desired outcome.
    Dummy class with not implemented `action` method:

    This can be

    - to recording the future `state` of the `Sample` or
    - to use the `state` of the `Sample` to recording a third-party-device (e.g., the mouse-cursor, etc.)
    - and more.
    """

    def __init__(self, name: (str, None) = "Agent", description: str = ""):
        """Constructor of an `Agent` instance

        :param name: A `Controller`-`Agent`'s name (str).
        :param description: Description of the agent (str, defaults to "").
        """

        self._action_data = []
        Controller.__init__(self, name=name, description=description)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: (str, None)):
        self._name = value if value is not None else "Agent"

    @property
    def comment(self) -> str:
        return self._comment

    @comment.setter
    def comment(self, value: str):
        self._comment = value

    def __str__(self):
        return f"<Feedback-Agent: {self.name}>"

    def to_dict(self):
        dict_repr = super().to_dict()
        dict_repr['class'] = '.'.join([self.get_module_name(), self.get_class_name()])
        return dict_repr

    @property
    def action_data(self):
        return self._action_data

    @action_data.setter
    def action_data(self, value):
        if not isinstance(value, list):
            if isinstance(value, dict):
                value = Agent.dict_to_list(value_dict=value)
            else:
                value = list(value)

        for i in range(len(value)):
            vi = value[i]

            if isinstance(vi, dict):
                timestamp = vi.pop('timestamp')

                try:
                    args = Agent.dict_to_list(value_dict=vi)

                except:
                    args = vi.values()

                value[i] = (timestamp, *args)

        self._action_data = value

    def append_action_data(self, value):
        self._action_data.append((time(), value))

    def action(self, state: (dict, ndarray)) -> (ndarray, tuple, object, None):
        """ Proposed `action` of the `Controller`-`Agent` (according to its internal policy) based on the `state`
            of a `Sample` (i.e., bio-signals of a `Subject`) to achieve a desired outcome.

        :param state: Dictionary or array_like state of the subject (i.e., bio-signals)
                      which are acquired with bio-sensory devices.
        :return: The recording action (this can be a vector of probability
                 amplitudes or more abstract quantities, depending on the
                 actual controller realization).
                 Also no action (None) can (should possibly) be taken.
        """
        raise NotImplementedError(f'{self.get_module_name()}.{self.get_class_name()}.action')

    def get_action(self, state):
        action = self.action(state)
        self.append_action_data(action)
        return action

    def dump_actions(self, filename, file_format=None, mode='w', key='action_data'):
        if file_format is None:
            __, extension = os.path.splitext(filename)
            if extension.lower() in ('.h5', '.hdf5', '.h5py'):
                file_format = 'h5'
            elif extension.lower() in ('.json'):
                file_format = 'json'
                raise NotImplementedError(f'file_format {file_format}')
            else:
                file_format = 'yml'
                raise NotImplementedError(f'file_format {file_format}')

        with h5py.File(filename, mode) as h5:
            g = h5.create_group(key)
            for i, (timestamp, action) in enumerate(self.action_data):
                g[f'{i}/timestamp'] = timestamp

                # store actions -- possibly None (ESC), otherwise (key, action_value) pairs
                for j, action_value in enumerate(action if hasattr(action, '__iter__') else [action]):
                    # check, whether action_value is value_dict (if None in case of key '.' -> save np.nan)
                    g[f'{i}/{j}'] = (action_value if action_value is not None else nan)

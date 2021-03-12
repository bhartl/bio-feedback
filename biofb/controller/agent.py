from numpy import ndarray
from biofb.session import Controller
from abc import ABCMeta, abstractmethod


class Agent(Controller, metaclass=ABCMeta):
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

    @abstractmethod
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
        pass

from biofb.io import Loadable


class Controller(Loadable):
    """ Controller base-datatype of the session sample. """

    def __init__(self, name: (str, None) = "Controller", description: str = "", **kwargs):
        """Constructor of Controller

        :param name: A `Controller`'s name (str).
        :param description: Description of the current `Setting` (str, defaults to "").
        """

        Loadable.__init__(self)

        self._name = None
        self.name = name

        self._description = None
        self.description = description

        self._kwargs = kwargs

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: (str, None)):
        self._name = value if value is not None else "Controller"

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

    def __str__(self):
        return f"<Controller: {self.name}>"

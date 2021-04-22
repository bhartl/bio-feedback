from biofb.io import Loadable
from pydoc import locate


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

    @classmethod
    def load(cls, value):
        try:
            assert isinstance(value, dict)
            specific_cls = value.pop('class')
            specific_kwargs = value.pop('kwargs', {})
            if specific_kwargs and isinstance(specific_kwargs, str):
                specific_kwargs = eval(specific_kwargs)

            if specific_cls and isinstance(specific_cls, str):
                specific_cls = locate(specific_cls)

            return specific_cls.load(dict(**value, **specific_kwargs))

        except (AssertionError, KeyError, AttributeError):

            return super().load(value)

    def to_dict(self):
        dict_repr = super().to_dict()
        if self.__class__ is not Controller:
            dict_repr['class'] = self.__class__.__name__

        return dict_repr

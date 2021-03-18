from biofb.io import Loadable
from biofb.session import Location
from biofb.session import Controller


class Setting(Loadable):
    """The overall setting of a sample measurement.

    This could be a standardised test scenario to capture/analyse bio-signals or a full bio-feedback session.
    """

    def __init__(self,
                 name: str = "setting",
                 controller: (Controller, dict, None) = None,
                 location: (Location, dict, None) = None,
                 description: str = "",
                 ):
        """Constructor of Setting

        :param name: A `Settings`'s identifier (str).
        :param controller: The bio-feedback `Controller` of the `Sample` (`Controller`, `dict` or None, defaults to None)
        :param location: The `Location` where the `Sample` is performed (`Location` or `dict`)
        :param description: Description of the current `Setting` (str, defaults to "").
        """

        Loadable.__init__(self)

        self._name = None
        self.name = name

        self._controller = None
        self.controller = controller

        self._location = None
        self.location = location

        self._description = None
        self.description = description

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def location(self) -> Location:
        return self._location

    @location.setter
    def location(self, value: (dict, Location)):
        self._location = Location.load(value)

    @property
    def controller(self) -> Controller:
        return self._controller

    @controller.setter
    def controller(self, value: (dict, Controller)):
        self._controller = Controller.load(value)

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

    def __str__(self):
        return f"<Setting: {self.name}>"

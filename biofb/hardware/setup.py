from biofb.io import Loadable
from biofb.hardware import Device


class Setup(Loadable):
    """A specific hardware setup which handles the involved devices."""

    def __init__(self, name: str, devices: (list, tuple), description=""):
        """Constructs a bio-controller hardware `Setup` instance.

        :param name: `name` of the hardware setup (str).
        :param devices: list of bio-controller hardware `Device`'s used in the hardware setup
                        (list or tuple of `Device`'s or representations thereof).
        :param description: description of the hardware `Setup` (str, defaults to `""`).
        """

        Loadable.__init__(self)

        self._name = None
        self.name = name

        self._devices = None
        self.devices = devices

        self._description = None
        self.description = description

        self._sample = None

    def __getitem__(self, key):
        """ Access channel via Channel-instance, name or id """

        if isinstance(key, Device):
            devices = [device for device in self.devices if device is key]
        elif isinstance(key, str):
            devices = [device for device in self.devices if device.name == key]
        elif isinstance(key, int):
            return self.devices[key]
        elif hasattr(key, '__iter__'):
            return [self[k] for k in key]

        else:
            raise NotImplementedError(f"Don't understand type `{type(key)}` of key `{key}`.")

        if len(devices) == 0:
            return None

        if len(devices) == 1:
            return devices[0]

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def devices(self) -> (list, tuple):
        return self._devices

    @devices.setter
    def devices(self, value):
        self._devices = []
        for v in value:
            d = Device.load(v)
            d._setup = self
            self._devices.append(d)

    @property
    def device_names(self) -> list:
        return [d.name for d in self.devices]

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

    def __str__(self) -> str:
        return f"<Setup: {self.name}>"

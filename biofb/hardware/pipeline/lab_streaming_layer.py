from biofb.io import Loadable
from biofb.hardware import Device
import pylsl


class LSLPipeline(Loadable):

    def __init__(self, devices=(), streams=(), **kwargs):
        Loadable.__init__(self)

        self._devices = None
        self.devices = devices

        self._streams = None
        self.streams = streams

    @property
    def devices(self):
        return self._devices

    @devices.setter
    def devices(self, value):
        if not hasattr(value, '__iter__'):
            value = [value]

        for device in value:
            assert isinstance(device, Device)

        self._devices = value

    @property
    def streams(self):
        return self._streams

    @streams.setter
    def streams(self, value):
        if not hasattr(value, '__iter__'):
            value = [value]

        self._streams = value

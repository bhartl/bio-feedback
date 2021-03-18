from biofb.io import Loadable
from biofb.hardware import Channel
from numpy import loadtxt, ndarray, asarray, concatenate
import importlib
from copy import deepcopy
from os.path import abspath


class Device(Loadable):
    """ Device used in a bio-controller hardware setup. """

    def __init__(self, name: str, channels: (tuple, list) = (), description: str = "", load_data_kwargs=(), data=None,
                 **parameters):
        """ Constructs a bio-controller hardware `Device` instance.

        :param name: `name` of the bio-interface hardware `Device` (str).
        :param channels: List of bio-interface hardware `Channel`s captured by the device
                         (`list` or `tuple`, defaults to `()`).
        :param load_data_kwargs: (Optional) Dictionary used as kwargs in if `load_data` is called. This is usefull in `biofb.session.Database` usage.
        :param data: (Optional) Device data array.
        :param description: Description of the bio-interface hardware `Device` (`str`, defaults to "").
        """

        Loadable.__init__(self)

        self._name = None
        self.name = name

        self._channels = None
        self.channels = channels

        self._description = None
        self.description = description

        self._load_data_kwargs = dict(load_data_kwargs)

        self.parameters = parameters
        self._setup = None

        # pipeline handling
        self._receiver = None
        self._transmitter = None

        self._data = data
        self.data = data

    def __getitem__(self, key):
        """ Access channel via Channel-instance, name or id """

        if isinstance(key, Channel):
            channels = [channel for channel in self.channels if channel is key]
        elif isinstance(key, str):
            channels = [channel for channel in self.channels if channel.name == key]
        elif isinstance(key, int):
            return self.channels[key]
        elif hasattr(key, '__iter__'):
            return [self[k] for k in key]

        else:
            raise NotImplementedError(f"Don't understand type `{type(key)}` of key `{key}`.")

        if len(channels) == 0:
            return None

        if len(channels) == 1:
            return channels[0]

        return channels

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def channels(self) -> (list, tuple):
        if self._channels is not None:
            for c in self._channels:
                c._device = self

        return self._channels

    @channels.setter
    def channels(self, value):
        self._channels = [
            v if isinstance(v, Channel) else Channel.load(v)
            for v in value
        ]

        for c in self.channels:
            c._device = self

    @property
    def n_channels(self) -> int:
        return len(self.channels)

    @property
    def data(self) -> (ndarray, None):
        if self._data is None:
            if self._setup is not None:
                return self._setup.get_device_data(device=self)

        return self._data

    @data.setter
    def data(self, value: (ndarray, None)):
        if self._data is None:
            if self._setup is not None:
                self._setup.set_device_data(data=value, device=self)
                return

        self._data = asarray(value) if value is not None else value

    def append_data(self, value: (ndarray, None)):
        if value is None:
            return

        if self._data is None:
            if self._setup is not None:
                self._setup.append_device_data(value=value, device=self)
                return

        data = self.data
        data = concatenate([data, value]) if data is not None else asarray(value)

        self.data = data

    @property
    def sampling_rates(self):
        return [c.sampling_rate for c in self.channels]

    @property
    def channel_names(self) -> list:
        return [d.name for d in self.channels]

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

    @classmethod
    def load(cls, value):
        if isinstance(value, cls):
            return value

        value = deepcopy(value)
        device_cls = value.pop('class', cls)
        device_src = value.pop('location', None)

        if device_cls != Device:

            if device_src is not None:
                device_module = importlib.import_module(device_src)
                device_cls = getattr(device_module, device_cls)

            else:
                device_cls = getattr(locals(), device_cls)

        return device_cls(**value)

    def load_data(self, filename, **kwargs):
        """ Load numpy array from file.

        :param filename: Path to read from
        :param kwargs: Forwarded keyword arguments to `numpy.loadtxt`.
        :returns: Loaded `numpy` array
        """
        return loadtxt(abspath(filename), **{**self._load_data_kwargs, **kwargs})

    def acquire_data(self):
        """

        :return:
        """

        raise NotImplementedError("Dataacquisition is device-specific.")

    def __str__(self) -> str:
        return f"<Device: {self.name}>"

    def plot(self, data=None, axes=None, label_by='label', figure_kwargs=(), **plot_kwargs):
        """ Plot provided data for all channel devices.

        :param data: (Optional) data for each channel (multiple data for each channel are possible,
                     dimensions must be `[n_channels, n_samples per channel, ...]`).
                     If data is None the hardware-setup sample-data are tried to be loaded.
        :param axes: (Optional) matplotlib axes object for each channel.
        :param label_by: (Optional) Channel attribute name which is used as y-label in the ax plot.
        :param figure_kwargs: (Optional) keywords dict object for `matplotlib.pyplot.subplots`
                              subplot generator in case `axes` is not provided
        :param plot_kwargs: (Optional) Keyword arguments for plot routine (forwarded to `biofb Channel plot` method.
        :returns: `axes` object.
        """

        if data is None:
            data = self.data
            assert data is not None, "No data arguments provided and no device data (or sample setup) defined."

        data = asarray(data)
        if data.shape[0] != len(self.channels):
            data = data.T

        plt = None
        if axes is None:
            import matplotlib.pyplot as plt
            f, axes = plt.subplots(len(self.channels), 1, **dict(figure_kwargs))

        for i in range(len(self.channels)):
            ax = self.channels[i].plot(data=data[i],
                                       ax=axes[i] if hasattr(axes, '__len__') else axes,
                                       label_by=label_by,
                                       **plot_kwargs)

            if i < len(self.channels) - 1:
                ax.set_xlabel(None)

        if plt is not None:
            plt.legend()
            plt.tight_layout()
            plt.show()

        return axes

    @property
    def receiver(self):
        return self._receiver

    @receiver.setter
    def receiver(self, value):
        from biofb.session import Controller
        from biofb.hardware.pipeline import Receiver

        if value is None:
            if self._receiver is not None:
                del self._receiver

            self._receiver = None

        if isinstance(value, tuple):
            receiver, kwargs = value
        else:
            receiver, kwargs = value, {}

        # update local variables such as "update_channels", "update_device", "update_sampling_rate"
        # based on load_data_kwargs defined during construction
        for k, v in self._load_data_kwargs.items():
            if k in locals():
                locals()[k] = v

        # prefer directly passed kwargs over load_data_kwargs
        update_device = kwargs.pop('update_device', locals().get('update_device', True))
        update_channels = kwargs.pop('update_channels', locals().get('update_channels', True))
        update_sampling_rate = kwargs.pop('update_sampling_rate', locals().get('update_sampling_rate', True))

        if isinstance(receiver, type):
            self._receiver = receiver.load(kwargs)
        else:
            self._receiver = receiver

        assert isinstance(self._receiver, Receiver) or isinstance(self._receiver, Controller)

        stream_info = self.receiver.stream_info

        if update_device:
            self.name = stream_info['meta_data']['name']

        if update_channels:
            assert stream_info['channels'] != []

            channels = []
            for channel in stream_info['channels']:
                channels.append(Channel.load(dict(sampling_rate=stream_info['meta_data']['sampling_rate'], **channel)))

            self.channels = channels

        if update_sampling_rate:
            for c in self.channels:
                c.sampling_rate = stream_info['meta_data']['sampling_rate']

    def receive_data(self, receiver: (None, Loadable)=None, **receiver_kwargs):
        """ """

        if receiver is None:
            assert self.receiver is not None, "No biofb.hardware.pipeline.Receiver specified."
            receiver = self.receiver

        else:
            assert self.receiver is None, "Only one receiver can be specified, close connection fist."
            self.receiver = (receiver, receiver_kwargs)
            receiver = self.receiver

        assert receiver is not None, "No receiver defined."

        timestamp, data_chunk = receiver.get_chunk()
        self.append_data(data_chunk)

        return timestamp, data_chunk

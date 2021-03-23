from biofb.io import Loadable
from biofb.hardware import Channel
from numpy import loadtxt, ndarray, asarray, concatenate
import importlib
from copy import deepcopy
from os.path import abspath
from biofb.pipeline import Receiver
from collections import defaultdict
import inspect


class Device(Loadable):
    """ Device used in a bio-controller hardware setup. """

    SENSOR_TO_CHANNEL_TYPE = {}
    """ Mapping of sensor specifications to labels that correspond to biofb.hardware.channels 
        (to load sensor-specific instances)
    """

    LABEL_TO_UNIT = defaultdict(lambda *args, **kwargs: '', [])
    """ Mapping of sensor labels that correspond to biofb.hardware.channels to predefined units
        of these sensors
    """

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
        """Number of channels"""
        return len(self.channels)

    @property
    def channel_names(self) -> list:
        return [d.name for d in self.channels]

    @property
    def sampling_rates(self):
        return [c.sampling_rate for c in self.channels]

    @property
    def sampling_rate(self):
        channel_sampling_rates = {c.sampling_rate for c in self.channels}
        assert len(channel_sampling_rates) == 1, "Multiple sampling rates specified."
        return channel_sampling_rates.pop()

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

    @property
    def data(self) -> (ndarray, None):
        """ `Device`-data property

        - if the `Device` is used without a `Setup`, the device hosts its own data array
        - if the `Device` is used in a hardware `Setup`, the `Setup` data is updated
        """
        if self._data is None:
            if self._setup is not None:
                return self._setup.get_device_data(device=self)

        return self._data

    @data.setter
    def data(self, value: (ndarray, None)):
        """ Set `Device`-data to provided values

        - If the `Device` is used without a `Setup`, the device hosts its own data array
        - If the `Device` is used in a hardware `Setup`, the `Setup` data is updated
        """
        if self._data is None:
            if self._setup is not None:
                self._setup.set_device_data(value=value, device=self)
                return

        self._data = asarray(value) if value is not None else value

    def append_data(self, value: (ndarray, None)):
        """ Append device data with provided values

        - If the device is used without a setup, the device hosts its own data array
        - If the device is used in a hardware setup, the corresponding setup data is updated
        """
        if value is None:
            return

        if self._data is None:
            if self._setup is not None:
                self._setup.append_device_data(value=value, device=self)
                return

        data = self.data
        data = concatenate([data, value]) if data is not None else asarray(value)

        self.data = data

    @classmethod
    def load(cls, value):
        """ Load a Device instance based on a dict-like, loadable representation

        :param value: dict-like, loadable representation of a Device (dict, yaml-file, path to dict-like object).
        :return: Either a new `Device` instance initialized from the `value` argument or
                 `value` if `value` is already a Device instance

        - If a **'class'** key-value pair is specified in the `value` argument, the devices-lookup-module
          (accessed via get_device_module) is searched for a proper Device class to load
        - If a **'location'** key-value pair is specified in the `value` argument, it specifies the location
          of the devices-lookup-module (in that way, new devices can be implemented outside of the `biofb` scope)
        """
        if isinstance(value, cls):
            return value

        value = deepcopy(value)
        device_cls = value.pop('class', cls)

        if device_cls != cls:

            if isinstance(device_cls, str):
                device_module = cls.get_devices_module(value.pop('location', None))
                device_cls = getattr(device_module, device_cls)

            assert inspect.isclass(device_cls)
            # device_cls = getattr(locals(), device_cls)

        return device_cls(**value)

    @classmethod
    def get_devices_module(cls, location: (str, None) = None):
        """ load devices-lookup-module

        :param
        """
        if location is None:
            location = 'biofb.hardware.devices'

        return importlib.import_module(location)

    @classmethod
    def find_devices_cls(cls, cls_name: str, location: str = None):
        """ Search for Devices classes in device-lookup-module `location` that either
            contain or is contained within the provided `cls_name`
            (useful to load Devices from data-streams)

        :param cls_name: Lookup string in device-lookup-module `location` for a matching Device class
        :param location: String specifier for the device-lookup-module `location`
        :return: Device type within the device-lookup-module `location` which first matches the `cls_name` specification
        """

        devices_module = cls.get_devices_module(location=location)

        for device_name, obj in inspect.getmembers(devices_module):
            if inspect.isclass(obj):
                if cls_name.lower() in device_name.lower():
                    return obj
                elif device_name.lower() in cls_name.lower():
                    return obj
                
            elif device_name == 'ALIASES' and isinstance(device_name, dict):
                for device_alias, device_cls in obj.items():
                    if cls_name.lower() in device_alias.lower():
                        return device_cls
                    elif device_alias.lower() in cls_name.lower():
                        return device_cls

        if cls is not Device:
            raise ModuleNotFoundError(f'could not identify specific Device based on cls_name `{cls_name}`')

        return cls

    def load_data(self, filename, **kwargs):
        """ Load numpy array from file and stores it in device data property

        :param filename: Path to file containing numpy data array
        :param kwargs: Forwarded keyword arguments to `numpy.loadtxt`.
        :returns: Loaded `numpy` array
        """
        self.data = loadtxt(abspath(filename), **{**self._load_data_kwargs, **kwargs})
        return self.data

    def __str__(self) -> str:
        return f"<Device: {self.name}>"

    def plot(self, data=None, axes=None, label_by='label', figure_kwargs={}, **plot_kwargs):
        """ Plot provided data for all channel devices.

        :param data: (Optional) data for each channel (multiple data for each channel are possible,
                     dimensions must be `[n_channels, n_samples per channel, ...]`).
                     If data is None the hardware-setup sample-data are tried to be loaded.
        :param axes: (Optional) matplotlib axes object for each channel.
        :param label_by: (Optional) Channel argument name which is used as y-label in the ax plot.
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
            figure_kwargs['sharex'] = figure_kwargs.get('sharex', True)
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

            import warnings
            warnings.simplefilter("ignore", UserWarning)
            plt.tight_layout()

            plt.show()

        return axes

    @property
    def receiver(self):
        """ bio-feedback pipeline Receiver property """
        return self._receiver

    @receiver.setter
    def receiver(self, value):
        """ bio-feedback pipeline Receiver setter

        :param value: Receiver instance or tuple of (Receiver-type, kwargs)

        - The **device-configuration is updated** according to the Receiver stream_info
          meta-data if an **'update_device'** key-value pair is provided in the kwargs
          (or has been defined in the `load_data_kwargs` property during construction)
        - The **device-channel-configuration is updated** according to the Receiver stream_info
          meta-data if an **'update_channels'** key-value pair is provided in the kwargs
          (or has been defined in the `load_data_kwargs` property during construction)
        - The **device-sampling_rate-configuration is updated** according to the Receiver stream_info
          meta-data if an **'update_sampling_rate'** key-value pair is provided in the kwargs
          (or has been defined in the `load_data_kwargs` property during construction)
        """
        if value is None:
            # stop and delete potential connected receivers
            if self._receiver is not None:

                try:
                    self._receiver.stop()
                except TypeError:
                    pass

                del self._receiver

            self._receiver = None
            return

        # extract arguments properly
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

        if isinstance(receiver, type):  # load receiver based on kwargs
            receiver = receiver.load(kwargs)
        else:
            receiver = receiver

        assert isinstance(receiver, Receiver), "Specified receiver must be of type `biofb.pipeline.Receiver`."
        self._receiver = receiver

        # get stream information
        stream_info = self.receiver.stream_info
        stream_name = stream_info['meta_data']['name']

        # update device meta-data
        if update_device:
            self.name = stream_name

        # update-channels (types and meta-data)
        if update_channels:
            assert stream_info['channels'] != [], f"No channel meta-data provided in stream `{stream_name}`"

            channels = []
            for channel in stream_info['channels']:
                channel = deepcopy(channel)
                channel_name = channel.pop('label')

                # try fetching channel label or type via the `sensor_to_label` method
                channel_type = channel.pop('type', self.sensor_to_channel_type(channel_name))

                if isinstance(channel_type, Channel):  # the mapping of the channel type is a Channel instance
                    # -> use the mapped Channel instance as blueprint for the device channel

                    channel = channel_type.copy()
                    channel.name = channel_name
                    channel.unit = channel.pop('unit', channel_type.unit)
                    assert channel_type.sampling_rate == stream_info['meta_data']['nominal_srate']

                else:  # use channel_type as label and create a new channel
                    channel_sampling_rate = stream_info['meta_data']['nominal_srate']
                    channel_unit = channel.pop('unit', self.LABEL_TO_UNIT[channel_type])

                    channel_dict = dict(
                        name=channel_name,
                        label=channel_type,
                        sampling_rate=channel_sampling_rate,
                        unit=channel_unit,
                        **channel
                    )

                    # Note: the 'label' key is used in Channel.load
                    # to potentially load a sensor-specific Channel instance
                    channel = Channel.load(channel_dict)

                channels.append(channel)

            self.channels = channels

        # update-sampling-rate (maybe get rid of this)
        if update_sampling_rate:
            for c in self.channels:
                c.sampling_rate = stream_info['meta_data']['nominal_srate']

    def receive_data(self, receiver: (None, Loadable)=None, **receiver_kwargs):
        """ Receive data from the specified `biofb.pipeline.Receiver` (blocking)
            and add the data to the device-data property

        :param receiver: (Optional) (i) Receiver instance
                         or (ii) to-be-initialized Receiver type (if no receiver has been specified)
        :param receiver_kwargs: (Optional) kwargs to initialize Receiver.
                                Only used, if Receiver argument is specified
        :return: tuple of (timestamp, sample-data-chunk) numpy arrays, representing the time-of-retrieval and
                 the retrieved channel data.
        """
        if receiver is None:  # assert that a receiver has been specified
            assert self.receiver is not None, "No biofb.hardware.pipeline.Receiver specified."
            receiver = self.receiver

        else:  # try initializing a new receiver
            assert self.receiver is None, "Only one receiver can be specified, close connection fist."
            self.receiver = (receiver, receiver_kwargs)
            receiver = self.receiver

        assert receiver is not None, "No receiver defined."

        # retrieve data, blocking
        timestamp, data_chunk = receiver.receive_data()

        # append to data property
        self.append_data(data_chunk)

        return timestamp, data_chunk

    @classmethod
    def sensor_to_channel_type(cls, sensor_name: str) -> (str, Channel):
        """ Mapping of channels to special channel labels or channel types.

        :param sensor_name: Name or label of sensor/channel which is looked up in
                            the Device's `SENSOR_TO_CHANNEL_TYPE` mapping
        :return: str- or Channel-instance-mapping in `SENSOR_TO_CHANNEL_TYPE`,
                 corresponding to the `sensor_name`

        If a sensor_name is not found, the function is called recursively, removing
        the last character of the sensor_name in the next function call
        (e.g. 'EEG 1' -> 'EEG ' -> 'EEG').
        This is repeated either until a proper channel mapping is found or an empty
        string "" is passed, resulting in a "CUSTOM" channel mapping.
        """

        if sensor_name in (None, (), {}, ""):
            return 'CUSTOM'

        if sensor_name not in cls.SENSOR_TO_CHANNEL_TYPE:
            return cls.sensor_to_channel_type(sensor_name[:-1])

        return cls.SENSOR_TO_CHANNEL_TYPE[sensor_name]


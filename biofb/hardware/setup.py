from biofb.io import Loadable
from biofb.hardware import Device
from numpy import ndarray, asarray, concatenate


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
        self._data = None

        self._receivers = None

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

    @classmethod
    def from_streams(cls, receiver_cls, streams, stream_kwargs=(), devices_location=None, **setup_kwargs):
        """ Initialize `Setup` instance based on the `biofb.pipeline.Receiver` multi-stream-configuration,
        each defined stream is related to a bio-feedback `Device`.

        :param receiver_cls: `Receiver` type used to initialize all `Receiver` instances related to the
                             available `Device` streams.
        :param streams: List of string identifiers for the available `Device` streams.
                        Each stream will is related to a `Device` in the hardware `Setup`.
        :param stream_kwargs: (i) List of `Receiver` keyword-arguments or (ii) dict representing global `Receiver`
                              keyword-arguments used to initialize `Receiver` instances related to the available
                              `Device` streams ..
        :param devices_location: `Device`-lookup-module locations used to search for possible specific `Device`s
                                 to load these `Device`s such as `Bioplux` or `Unicorn` (defaults to
                                 `biofb.hardware.devices`).
        :param setup_kwargs: Keyword-arguments used to initialize the hardware `Setup`.

        :return: `Setup` instance based on the `biofb.pipeline.Receiver` stream-configuration
        """
        devices = []

        try:
            stream_kwargs = dict(stream_kwargs)
        except TypeError:
            pass

        for i, stream in enumerate(streams):

            # initialize Receiver instance
            kwargs = stream_kwargs if isinstance(stream_kwargs, dict) else stream_kwargs[i]
            receiver = receiver_cls(stream=stream, **kwargs)

            # initialize device, try to load specific device based on stream-name
            device = Device.load(
                value={'name': stream,
                       'class': Device.find_devices_cls(stream),
                       'location': devices_location,
                       'description': f'`Setup.from_stream` device.'}
            )

            device.receiver = receiver

            if receiver.verbose:
                print('Stream infos -> {device}: ')
                for k, v in receiver.stream_info['meta_data'].items():
                    print(f'  {k}: {v}')

                print('\nChannel infos: ')
                for channel_stream, channel_device in zip(receiver.stream_info['channels'], device.channels):
                    print(f'  stream channel: {channel_stream} -> device channel: {channel_device}')

            devices.append(device)

        return cls.load(value={'devices': devices, **setup_kwargs})

    def stop(self):
        """ Stop potentially started data-`Receiver`'s """
        if self._receivers is not None:
            for r in self._receivers:
                r.stop()

            self._receivers = None

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

        if isinstance(value, dict):
            value = Loadable.dict_to_list(value)

        for v in value:
            d = Device.load(v)
            d._setup = self
            self._devices.append(d)

    @property
    def device_names(self) -> list:
        return [d.name for d in self.devices]

    @property
    def n_devices(self) -> int:
        return len(self.devices)

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

    def __str__(self) -> str:
        return f"<Setup: {self.name}>"

    @property
    def data(self) -> list:
        """ `Setup`-data property: a list of device-data

        - if the `Setup` is used without a `Sample`, the `Setup` hosts its own data list of device-data arrays
        - if the `Setup` is used in a `Sample`-session, the `Sample`-data is updated
        """
        if self._data is None:
            if self._sample is not None:
                return self._sample.data

            self._data = [None]*self.n_devices
            return self._data

        return self._data

    @data.setter
    def data(self, value: list):
        """ set `Device`-data list as the `Setup`-data property

        - if the `Setup` is used without a `Sample`, the `Setup` hosts its own data list of device-data arrays
        - if the `Setup` is used in a `Sample`-session, the `Sample`-data is updated
        """
        if self._data is None:
            if self._sample is not None:
                self._sample.data = value
                return

        self._data = value

    def get_device_data(self, device: (Device, int, str)) -> (ndarray, None):
        """ Get data of specific `Device`

        :param device: `Device` instance, label or id
        :return: `Device`-data array or None
        """
        if not isinstance(device, Device):
            device = self[device]

        for i, device_i in enumerate(self.devices):
            if device_i is not device:
                continue

            return self.data[i]

        raise AttributeError(f"Device {device} not found.")

    def set_device_data(self, value: (None, ndarray), device: (Device, int, str)):
        """ Set data of specific `Device`

        :param value: `Device`-specific data array
        :param device: `Device` instance, label or id
        """
        if not isinstance(device, Device):
            device = self[device]

        for i, device_i in enumerate(self.devices):
            if device_i is not device:
                continue

            if value is not None:
                value = asarray(value)

            self.data[i] = value
            return

        raise AttributeError(f"Device {device} not found.")

    def append_device_data(self, value: (None, ndarray), device: (Device, int, str)):
        """ Append/Concatenate data to specific `Device`-data

        :param value: `Device`-specific (to be appended) data array
        :param device: `Device` instance, label or id
        """
        if not isinstance(device, Device):
            device = self[device]

        for i, device_i in enumerate(self.devices):
            if device_i is not device:
                continue

            data = self.data
            data[i] = concatenate([data[i], value]) if data[i] is not None else asarray(value)
            self.data = data

            return

        raise AttributeError(f"Device {device} not found.")

    def receive_data(self, receivers: (list, None) = None, receivers_kwargs: (None, list, dict) = None):
        """ Retrieve sample-data(-chunk) from the specified associated list of receivers related to
            each device (blocking, until a sample-data(-chunk) has been retrieved for each device)

        :param receivers: (Optional) list of `Receiver` instances/types which are assigned to the
                          related `Devices` of the hardware `Setup` (see also `receivers_kwargs`
                          argument).
        :param receivers_kwargs: (Optional) dict or list of kwargs used in the `Receiver` initialization.
                                 Only used if `receivers` is specified.
                                 If dict is provided, all `receivers` are instantiated with the same
                                 `receivers_kwargs`; otherwise, each element of `receivers` is related
                                 to the corresponding element in `receivers_kwargs`
        :return: list of `Device.receive_data()` results, i.e.,
                 list of tuples of (timestamps_device_i, sample_chunk_device_i) arrays, specifying
                 the timestamps and retrieved device data.

        The data-retrieval of each Device is performed in separate `multiprocessing.Process`es
        (using the `Retriever`s' background data-retrieval functionality, eventually, the `stop()` method
        should be called).
        """

        if receivers is None:
            assert all(device.receiver is not None for device in self.devices), "No `biofb.hardware.pipeline." \
                                                                                "Receiver` specified."

        else:
            assert all(device.receiver is None for device in self.devices), "Only one receiver perdevice can be " \
                                                                            "specified, close connections fist."
            for i, device in enumerate(self.devices):
                receiver = receivers[i]

                kwargs = {}
                if receivers_kwargs is not None:
                    kwargs = receivers_kwargs if isinstance(receivers_kwargs, dict) else receivers_kwargs[i]

                device.receiver = (receiver, kwargs)

        if self._receivers is None:

            self._receivers = [d.receiver for d in self.devices]
            [r.start() for r in self._receivers]

        chunk_data = [receiver.pull_data() for receiver in self._receivers]

        # here data-preprocessing can be done:
        # - synchronize data of different devices using the time-stamps
        # - apply filters
        # - ...
        for (time, value), device in zip(chunk_data, self.devices):
            self.append_device_data(value=value, device=device)

        return chunk_data

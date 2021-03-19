from biofb.io import Loadable
from numpy import ndarray
from abc import ABCMeta, abstractmethod
from multiprocessing import Process, Queue, Event
from queue import Empty
from collections import defaultdict
import time

STREAM_TYPES = ('name', 'type', 'hostname')


class Transmitter(Loadable, metaclass=ABCMeta):
    """ Abstract Device-Transmitter class for data-acquisition

    Methods to overwrite:

    - is_connected
    - connect
    - stream_info
    - put_chunk
    """

    def __init__(self, device: Loadable, stream: (str, None) = None, channels=None,
                 stream_type: str = 'name', verbose: bool = True,
                 **kwargs):
        """ Construct a Transmitter instance

        :param stream: defaults to device name
        :param device:
        :param channels:
        :param stream_type:
        :param verbose:
        :param kwargs:
        """
        Loadable.__init__(self, )

        self._kwargs = kwargs

        self._stream = None
        self.stream = stream

        self._device = None
        self._channels = None
        self.device = device
        if channels is not None:
            self.channels = channels

        self._stream_type = None
        self.stream_type = stream_type

        self._verbose = None
        self.verbose = verbose

        self._pusher = None
        self._queue = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._pusher is not None:
            try:
                self._pusher.terminate()
                self._pusher = None
            except AssertionError:
                pass

        if self._queue is not None:
            while not self._queue.empty():
                try:
                    self._queue.get(timeout=0.001)
                except (TimeoutError, Empty):
                    pass

            self._queue.close()
            self._queue = None

    def stop(self):
        if self._pusher is not None and self._queue is not None:
            self.__exit__(None, None, None)

    def to_dict(self):
        return dict(stream=self.stream,
                    stream_type=self.stream_type,
                    device=self.device,
                    channels=self.channels,
                    verbose=self.verbose,
                    **self._kwargs)

    @property
    def stream(self) -> str:
        return self._stream

    @stream.setter
    def stream(self, value: (str, None)):
        self._stream = value  # if value is not None else self.device['name']

    @property
    def device(self) -> defaultdict:
        return self._device

    @property
    def channels(self) -> [defaultdict]:
        return self._channels

    @channels.setter
    def channels(self, value: [defaultdict]):
        assert all(isinstance(c, defaultdict) or isinstance(c, dict) for c in value)
        self._channels = value

    @device.setter
    def device(self, value: Loadable):
        from biofb.hardware import Device
        from biofb.controller import Agent

        if isinstance(value, Device):
            self.channels = self.channels_to_list_of_dicts(value.channels)
        elif isinstance(value, Agent):
            raise NotImplementedError("transmit controller actions or session output.")

        kwargs = {
            'channel_format': self._kwargs.get('channel_format', 'float32'),
        }
        self._device = self.device_to_dict(value, stream=self.stream, **kwargs)

    @staticmethod
    def channels_to_list_of_dicts(channels: list) -> [defaultdict]:
        """ Serialize biofb.hardware.channel instances for the specific transmitter

        :return: list of biofb.hardware.channel instances that are to be
                 serialized for the specific transmitter
        """

        from biofb.hardware import Channel

        list_of_channel_dicts = []
        for i, c in enumerate(channels):
            channel_dict = defaultdict()

            try:
                name = c.name if isinstance(c, Channel) else c.get('name', f'CH{i}')
                channel_dict['label'] = name
            except (TypeError, AttributeError) as ex:
                channel_dict['label'] = f'CH{i}'

            try:
                label = c.label if isinstance(c, Channel) else c['label']
                channel_dict['type'] = label
            except (TypeError, AttributeError):
                pass

            try:
                unit = c.unit if isinstance(c, Channel) else c['unit']
                channel_dict['unit'] = unit
            except (TypeError, AttributeError):
                pass

            try:
                channel_type = c.__class__.__name__ if isinstance(c, Channel) else c['type']
                channel_dict['type'] = channel_type
            except (TypeError, AttributeError):
                pass

            list_of_channel_dicts.append(channel_dict)

        return list_of_channel_dicts

    @staticmethod
    def device_to_dict(device: Loadable, stream: str, channel_format: str = 'float32') -> defaultdict:
        from biofb.hardware import Device
        from biofb.controller import Agent

        device_dict = defaultdict()

        if isinstance(device, Device):
            device_dict['name'] = stream
            device_dict['type'] = device.__class__.__name__
            device_dict['channel_count'] = device.n_channels
            device_dict['nominal_srate'] = device.sampling_rate
            device_dict['channel_format'] = channel_format
            device_dict['source_id'] = device.name

        elif isinstance(device, Agent):
            raise NotImplementedError('Agent device')

        else:
            assert isinstance(device, dict) or isinstance(device, defaultdict)

            device_dict['name'] = device['name']
            device_dict['type'] = device['type']
            device_dict['channel_count'] = device['channel_count']
            device_dict['nominal_srate'] = device['nominal_srate']
            device_dict['channel_format'] = device['channel_format']
            device_dict['source_id'] = device['source_id']

        return device_dict

    @property
    def stream_type(self) -> str:
        return self._stream_type

    @stream_type.setter
    def stream_type(self, value: str):
        assert value in STREAM_TYPES
        self._stream_type = value

    @property
    def verbose(self) -> bool:
        return self._verbose

    @verbose.setter
    def verbose(self, value: bool):
        self._verbose = value

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """ Boolean property specifying whether the stream is connected

        :return: True if connected, False otherwise
        """
        pass

    @abstractmethod
    def connect(self) -> tuple:
        """ Connect to specified stream

        :return: (stream object, stream info dictionary) tuple
        """
        pass

    def augment_sampling_rate(self, augmented_sampling_rate: int = 0):
        """ sleep for 1./augmented_sampling_rate if augmented_sampling_rate > 0
            or if augmented_sampling_rate has been defined during construction.

        :param augmented_sampling_rate: Positive integer sends process sleeping for time, reciprocal to specified value.
        """

        if not augmented_sampling_rate:
            augmented_sampling_rate = self._kwargs.get('augment_sampling_rate', 0)
            if isinstance(augmented_sampling_rate, bool) and augmented_sampling_rate:
                augmented_sampling_rate = self.device['nominal_srate']

        if augmented_sampling_rate:
            time.sleep(1./abs(augmented_sampling_rate))

    @property
    @abstractmethod
    def stream_info(self) -> [dict, list]:
        """ Get stream information

        :return (stream info dict, list of channel info) tuple of the current stream
        """
        pass

    @abstractmethod
    def transmit_data(self, data: ndarray):
        """ Put data chunk on the transmission stream

        :param data: array-like data chunk
        """
        pass

    @classmethod
    def start_transmitting_data(cls, queue, connectin_established_event, **kwargs):
        """ Transmit data that are pushed on the queue in the main process via the push_data method

        Data that have been pushed (via push_data(...)) are collected by the transmitter
        and transmitted via put_chunk(...).

        :param queue: multiprocessing Queue to get to-be-transmitted data from the main process
        :param connectin_established_event:
        :param kwargs:
        """

        transmitter = cls(**kwargs)
        transmitter._queue = queue

        if transmitter.verbose:
            print(f'Establish connection to stream {transmitter.stream} ... ')

        transmitter.connect()

        if transmitter.verbose:
            print('Connection established')

        connectin_established_event.set()

        while True:
            chunk_data = transmitter._queue.get()
            transmitter.transmit_data(chunk_data)

    def start(self):
        """ Start transmitting data as background process

        starts Transmitter.start_transmitting_data class method as multiprocessing.Process

        Data that have been pushed (via push_data(...)) are collected by the transmitter
        and sent via put_chunk(...).
        """
        self._queue = Queue()
        self._connectin_established_event = Event()
        self._pusher = Process(name='transmitter',
                               target=type(self).start_transmitting_data,
                               args=(self._queue, self._connectin_established_event),
                               kwargs=self.to_dict())
        self._pusher.start()
        self._connectin_established_event.wait()
        return self

    def push_data(self, data: ndarray):
        """ Push data chunk to transmitting queue (for multiprocessing)

        :param data: Array-like data chunk
        """
        assert self._pusher is not None, "Background streaming needs to be `start`ed, use `receiver.start()`."
        assert self._queue is not None, "Background streaming needs to be `start`ed."
        self._queue.put(data)
        self.augment_sampling_rate()

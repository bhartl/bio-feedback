from biofb.io import Loadable
from numpy import ndarray
from abc import ABCMeta, abstractmethod
from multiprocessing import Process, Queue
from queue import Empty


STREAM_TYPES = ('name', 'type', 'hostname')


class Receiver(Loadable, metaclass=ABCMeta):
    """ Abstract Device-Receiver class for data-acquisition

    Methods to overwrite:

    - is_connected
    - connect
    - stream_info
    - get_chunk
    """

    def __init__(self, stream: str, stream_type: str = 'name', verbose: bool = True, **kwargs):
        """ Construct a Receiver instance

        :param stream:
        :param stream_type:
        :param verbose:
        :param kwargs:
        """
        Loadable.__init__(self, )

        self._stream = None
        self.stream = stream

        self._stream_type = None
        self.stream_type = stream_type

        self._verbose = None
        self.verbose = verbose

        self._kwargs = kwargs

        self._puller = None
        self._queue = None

    def close(self):
        if self._puller is not None:
            self._puller.terminate()
            self._puller = None

        if self._queue is not None:
            while not self._queue.empty():
                try:
                    self._queue.get(timeout=0.001)
                except (TimeoutError, Empty):
                    pass

            self._queue.close()
            self._queue = None

    def to_dict(self):
        return dict(stream=self.stream,
                    stream_type=self.stream_type,
                    verbose=self.verbose,
                    **self._kwargs)

    @property
    def stream(self):
        return self._stream

    @stream.setter
    def stream(self, value):
        self._stream = value

    @property
    def stream_type(self):
        return self._stream_type

    @stream_type.setter
    def stream_type(self, value):
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
        """ connect to specified stream

        :return: (stream object, stream info dictionary) tuple
        """
        pass

    @property
    @abstractmethod
    def stream_info(self) -> [dict, list]:
        """ get stream information

        :return (stream info dict, list of channel info) tuple of the current stream
        """
        pass

    @abstractmethod
    def receive_data(self) -> [ndarray, ndarray]:
        """ get data chunk from the transmission stream

        :return (timestamp-ndarray, data-ndarray) tuple for a pulled data chunk from the stream
        """
        pass

    @classmethod
    def start_receiving_data(cls, queue, **kwargs):
        receiver = cls(**kwargs)
        receiver.connect()
        receiver._queue = queue

        try:
            while True:
                chunk_data = receiver.receive_data()
                receiver._queue.put(chunk_data)
        except Exception as ex:
            print(ex)

    def start(self):
        self._queue = Queue()
        self._puller = Process(name='pull data',
                               target=type(self).start_receiving_data,
                               args=(self._queue, ),
                               kwargs=self.to_dict())
        self._puller.start()
        return self

    def pull_data(self) -> [ndarray, ndarray]:
        assert self._puller is not None, "Background streaming needs to be `start`ed, use `receiver.start()`."
        assert self._queue is not None, "Background streaming needs to be `start`ed."
        return self._queue.get()

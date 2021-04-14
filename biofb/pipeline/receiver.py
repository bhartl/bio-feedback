from biofb.io import Loadable
from numpy import ndarray
from abc import ABCMeta, abstractmethod
from multiprocessing import Process, Queue
from queue import Empty
from biofb.pipeline import STREAM_TYPES


class Receiver(Loadable, metaclass=ABCMeta):
    """ Abstract Device-Receiver class for data-acquisition

    - A stream definition is used to unravel device information
    - Data can be pulled/received by the Receiver instance

    The receiver can be started in the background to acquire data-chunks from a streaming source:

    - use the start() method to start receiving (and end the receiving with stop())
      or, alternatively, declare the Receiver in a `with` environment
    - use pull_data() to extract a chunk of data (blocking but filled by a worker process in the background)

    Methods to override:

    - is_connected
    - connect
    - stream_info
    - get_chunk
    """

    def __init__(self, stream: str, stream_type: str = 'name', verbose: bool = True, **kwargs):
        """ Construct a Receiver instance

        :param stream: stream specifier, either a name of a stream, the hostname of a streaming-machine,
                       the type of a stream
        :param stream_type: String, specifying the stream type,
                            i.e. whether the provided stream is stream-name, a stream-host, a stream-type, ...
        :param verbose: Boolean controlling whether the Receiver instance prints status messages (if True).
        :param kwargs: possible kwargs to be used in derived classes
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

    def to_dict(self) -> dict:
        """ Create dict representation of the current Receiver instance

        :return: dict representation of the Receiver instance
        """
        return dict(stream=self.stream,
                    stream_type=self.stream_type,
                    verbose=self.verbose,
                    **self._kwargs)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._puller is not None:
            self._puller.terminate()
            self._puller = None

        if self._queue is not None:
            while not self._queue.empty():
                try:
                    self._queue.get(timeout=1e-12)
                except (TimeoutError, Empty):
                    pass

            self._queue.close()
            self._queue = None

    def __str__(self):
        return f"<{self.__class__.__name__}: {self.stream}-stream>"

    @property
    def stream(self) -> str:
        """ Stream specification property """
        return self._stream

    @stream.setter
    def stream(self, value: str):
        """ Stream specification property

        :param value: the specification of the stream name/hostname/type (str)
        """
        self._stream = value

    @property
    def stream_type(self) -> str:
        """ Stream-type specification property """
        return self._stream_type

    @stream_type.setter
    def stream_type(self, value):
        """ Stream type specification property

        :param value: the type of the stream, needs to be an element of `Receiver.STREAM_TYPES`
        """
        assert value in STREAM_TYPES
        self._stream_type = value

    @property
    def verbose(self) -> bool:
        """ Boolean property controlling whether the Receiver prints status messages """
        return self._verbose

    @verbose.setter
    def verbose(self, value: bool):
        """ Boolean property controlling whether the Receiver prints status messages

        :param value: True if Receiver should be verbose, False otherwise
        """
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
        """ receive data chunk from the established stream connection

        :return (timestamp-ndarray, data-ndarray) tuple for a pulled data chunk from the stream
        """
        pass

    def start(self):
        """ Start a Receiver instance in the background which fills the data-queue with samples

        Data can be pulled using the pull_data() method on the calling Receiver instance

        :return: The calling Receiver instance
        """

        self._queue = Queue()
        self._puller = Process(name='pull data',
                               target=type(self).__start_receiving_data,
                               args=(self._queue, ),
                               kwargs=self.to_dict())
        self._puller.start()
        return self

    @classmethod
    def __start_receiving_data(cls, queue: Queue, **kwargs):
        """ Class-method which creates, connects and starts a `Receiver`
        of type `cls` based on the `kwargs` specification.

        Supposed to be called from within the `start()` method,
        i.e. as a seperate `multiprocessing.Process` with then
        communicates with the main process via the specified
        `queue`.

        :param queue: `multiprocessing.Queue` instance used for data-communication between main and child process.
        :param kwargs: dict representation of to be generated Receiver (`cls`) instance
        """
        receiver = cls(**kwargs)
        receiver.connect()
        receiver._queue = queue

        try:
            while True:
                chunk_data = receiver.receive_data()
                receiver._queue.put(chunk_data)
        except Exception as ex:
            print(ex)

    def pull_data(self) -> [ndarray, ndarray]:
        """ Pull received sample data from the data-queue

        :return: tuple of (timestamp, sample-data) data-chunks of the specified chunk-size """

        assert self._puller is not None, "Background streaming needs to be `start`ed, use `receiver.start()`."
        assert self._queue is not None, "Background streaming needs to be `start`ed."
        return self._queue.get()

    def stop(self):
        """ Stop background receiving and cleanup started processes and queues """

        if self._puller is not None and self._queue is not None:
            self.__exit__(None, None, None)

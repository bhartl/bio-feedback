from pylsl import StreamInlet, resolve_stream
from biofb.pipeline import Receiver
from numpy import ndarray, asarray, empty


class LSLReceiver(Receiver):
    """ Class to connect to a Lab Streaming Layer stream and receive data using pylsl

        See also the official
        `example <https://github.com/chkothe/pylsl/blob/master/examples/ReceiveData.py>`_
        to `ReceiveData.py` with `pylsl`.
        """

    def __init__(self, stream: str, stream_type: str = 'name', chunk_size=1., pull_chunks=False, verbose=True,
                 **kwargs):
        """ Creates an LSLReceiver instance

        :param stream: String specification of the stream
        :param stream_type: Type of the stream (name/hostname/type)
        :param chunk_size: Fraction of a the streams sampling rate (if chunk_size is float) or the number of
                           data-samples (if chunk_size is int) which are considered a chunk of samples
        :param pull_chunks: Boolean controlling whether sample data should be pulled as chunks of samples (if True)
                            of sample-by-sample otherwise
        :param verbose: Boolean controlling whether the Receiver prints status messages (if True)
        :param kwargs: Optional keyword arguments
        """
        Receiver.__init__(self, stream=stream, stream_type=stream_type, verbose=verbose, **kwargs)

        self._chunk_size = None
        self.chunk_size = chunk_size

        self._pull_chunks = None
        self.pull_chunks = pull_chunks

        self._stream_inlet = None
        self._stream_info = None

    def to_dict(self):
        """ Create dict representation of the current LSLReceiver instance

        :return: dict representation of the Receiver instance
        """
        data = Receiver.to_dict(self)
        lsl_receiver_data = dict(
            chunk_size=self.chunk_size,
            pull_chunks=self.pull_chunks,
        )

        return dict(**data, **lsl_receiver_data)

    @property
    def stream_inlet(self) -> StreamInlet:
        """ `pylsl.StreamInlet` property, used to receive data from the stream

        Tries to establish a connection if necessary

        :return: `pylsl.StreamInlet` instance of the LSL-stream
        """
        if not self.is_connected:
            self.connect()

        return self._stream_inlet

    @property
    def stream_info(self) -> dict:
        """ Stream-info property, specifying information about the pylsl-stream

        Tries to establish a connection if necessary

        :return: dict-representation of the established LSL-stream
        """
        if not self.is_connected:
            self.connect()

        return self._stream_info

    @property
    def is_connected(self) -> bool:
        """ Boolean property specifying whether an LSL stream connection is established """
        return self._stream_inlet is not None

    @property
    def chunk_size(self) -> (float, int):
        """ Sample-data chunk size property

         - if float: the fraction of the sampling rate
         - if int: the number of data-samples

         which are considered a chunk
         """
        return self._chunk_size

    @chunk_size.setter
    def chunk_size(self, value: (float, int)):
        """ Sample-data chunk size property

         - if float: the fraction of the sampling rate
         - if int: the number of data-samples

         which are considered a chunk
         """
        self._chunk_size = value

    @property
    def pull_chunks(self) -> bool:
        """ Boolean property (getter) controlling whether the LSLReceiver tries to receive data in chunks
            (usually faster)

        Note: The chunk size of the received data using pylsl differs from the LSLReceiver.chunk_size specification.
              When using the receive_data() or pull_data() methods, data-chunks of shape `chunk_size x n_channels`
              will be returned.
        """
        return self._pull_chunks

    @pull_chunks.setter
    def pull_chunks(self, value: bool):
        """ Boolean property (setter) controlling whether the LSLReceiver should tries to receive data in chunks
            (usually faster)

        Note: The chunk size of the received data using pylsl differs from the LSLReceiver.chunk_size specification.
              When using the receive_data() or pull_data() methods, data-chunks of shape `chunk_size x n_channels`
              will be returned.
        """
        self._pull_chunks = value

    def receive_data(self) -> [ndarray, ndarray]:
        """ Receive a data chunk from the LSL (blocking)

        Tries to establish a connection if necessary

        :return: tuple of (timestamps, data-sample)-chunks
        """
        if not self.is_connected:
            self.connect()

        return LSLReceiver.get_data_chunk(stream_inlet=self.stream_inlet,
                                          stream_info=self.stream_info,
                                          chunk_size=self.chunk_size,
                                          pull_chunks=self.pull_chunks)

    def connect(self) -> [StreamInlet, dict]:
        """ Connect to the specified LSL stream

        :return: tuple of (`pylsl.StreamInlet`-instance, stream-info dict-repr), specifying the
                 (i) stream-connection and meta-data about the stream.
        """
        if self._verbose:
            print(f'try connecting to stream `{self.stream}` of type `{self.stream_type}` ...')

        stream_inlet, info = LSLReceiver.connect_to_lsl_stream(stream_name=self.stream,
                                                               stream_type=self.stream_type)

        if self._verbose:
            if stream_inlet is not None:
                print(f'connection to stream `{self.stream}` of type `{self.stream_type}` established.')
            else:
                print(f'could not establish connection to stream `{self.stream}` of type `{self.stream_type}`.')

        self._stream_inlet = stream_inlet
        self._stream_info = info

        return self.stream_inlet, self.stream_info

    @staticmethod
    def connect_to_lsl_stream(stream_name: str, stream_type: str) -> [StreamInlet, dict]:
        """ Connect to an LSL stream using pylsl

        :param stream_name: String specifier of the LSL-stream
        :param stream_type: String, specifying the type of the stream (name/type/hostname)
        :return: tuple of (`pylsl.StreamInlet`-instance, stream-info dict-repr), specifying the
                 (i) stream-connection and meta-data about the stream.
        """
        streams = resolve_stream(stream_type, stream_name)

        # create a new inlet to read from the stream
        stream_inlet = StreamInlet(streams[0])

        stream_meta_data, stream_channels = LSLReceiver.get_lsl_metadata(stream_inlet)

        info = dict(meta_data=stream_meta_data, channels=stream_channels)

        return stream_inlet, info

    @staticmethod
    def get_lsl_metadata(stream_inlet: StreamInlet, ) -> [dict, list]:
        """ Get LSL-stream meta-data (stream-information) of a `pylsl.StreamInlet` object

        :param stream_inlet: `pylsl.StreamInlet` instance, specifying an LSL connection
        :return: tuple of (meta_data, channels) dictionaries
        """
        stream_meta_data = {}
        stream_channels = []

        # extract general information about the stream
        stream_info = stream_inlet.info()

        stream_meta_data['name'] = stream_info.name()
        stream_meta_data['mac'] = stream_info.type()
        stream_meta_data['host'] = stream_info.hostname()
        stream_meta_data['channel_count'] = stream_info.channel_count()
        stream_meta_data['channel_format'] = stream_info.channel_format()
        stream_meta_data['nominal_srate'] = stream_info.nominal_srate()
        stream_meta_data['source_id'] = stream_info.source_id()
        stream_meta_data['session_id'] = stream_info.session_id()
        stream_meta_data['created_at'] = stream_info.created_at()
        stream_meta_data['version'] = stream_info.version()

        try:
            # extract channel specific information of the stream (using the .desc() method on the stream_info object
            channels = stream_info.desc().child("channels").child("channel")

            for i in range(stream_meta_data['channel_count']):  # loop through all available channels
                channel_label = channels.child_value("label")  # get the channel type (e.g., ECG, EEG, ...)
                channel_unit = channels.child_value("unit")  # get the channel unit (e.g., mV, ...)
                channel_type = channels.child_value("type")  # get the channel type (e.g., ECG, EEG, ...)

                stream_channels.append({'label': channel_label,
                                        'type': channel_type,
                                        'unit': channel_unit})
                channels = channels.next_sibling()

        except TypeError:
            pass

        return stream_meta_data, stream_channels

    @staticmethod
    def get_data_chunk(stream_inlet: StreamInlet, stream_info: dict, chunk_size: (float, int),
                       pull_chunks=True) -> [ndarray, ndarray]:
        """ Receive a data-chunk from the provided StreamInlet instance

        :param stream_inlet: pylsl.StreamInlet instance used to pull data from the LSL
        :param stream_info: stream-info dict-representation, providing meta-data about
                            the number of channels, ..., necessary to receive the data
        :param chunk_size: Fraction of a the streams sampling rate (if float) or the number of
                           data-samples (if int) which are considered a chunk of samples
        :param pull_chunks: Boolean controlling, whether data are pulled as chunks from the LSL (if True)
                            or sample-by-sample otherwise (the former is usually faster but the number
                            of received data-points can differ from the specified chunk-size)
        :return: tuple of (timestamp, chunk-of-received-samples) `numpy.ndarray`s,
                 the len of the chunk is defined by `chunk_size` and `pull_chunks`
                 attributes
        """

        if isinstance(chunk_size, float):
            chunk_size = int(stream_info['meta_data']['nominal_srate'] * chunk_size)
        assert isinstance(chunk_size, int)

        # if the data are pulled as chunks, we us a list to append new chunks
        # if the data are pulled as samples, we know in advance, how many samples we expect
        samples = [] if pull_chunks else empty((chunk_size, stream_info['meta_data']['channel_count']))
        timestamp = [] if pull_chunks else empty(chunk_size)
        sample_count = 0

        if pull_chunks:                       # pull data from the inlet as chunks
            while len(samples) < chunk_size:  # until at least a number of 'chunk_size' samples are received
                sample, chunk_timestamp = stream_inlet.pull_chunk()

                if len(sample) > 0:           # also no-data can be received, we await the next chunk then
                    samples.extend(sample)
                    timestamp.extend(chunk_timestamp)

        else:
            while sample_count < chunk_size:  # pull data as single samples from the inlet
                sample, sample_timestamp = stream_inlet.pull_sample()

                samples[sample_count, :] = sample           # assign the sample data
                timestamp[sample_count] = sample_timestamp  # assigned the time-stamps
                sample_count += 1

        return asarray(timestamp), asarray(samples)

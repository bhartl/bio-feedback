from pylsl import StreamInlet, resolve_stream
from biofb.pipeline import Receiver
from numpy import ndarray, asarray, empty


class LSLReceiver(Receiver):
    """ Receiver class of data-chunks from the Lab Streaming Layer """

    def __init__(self, stream: str, stream_type: str = 'name', chunk_size=1., pull_chunks=False, verbose=True, **kwargs):
        Receiver.__init__(self, stream=stream, stream_type=stream_type, verbose=verbose, **kwargs)

        self._chunk_size = None
        self.chunk_size = chunk_size

        self._pull_chunks = None
        self.pull_chunks = pull_chunks

        self._stream_inlet = None
        self._stream_info = None

    def to_dict(self):
        data = Receiver.to_dict(self)
        lsl_receiver_data = dict(
            chunk_size=self.chunk_size,
            pull_chunks=self.pull_chunks,
        )

        return dict(**data, **lsl_receiver_data)

    @property
    def stream_inlet(self):
        if not self.is_connected:
            self.connect()

        return self._stream_inlet

    @property
    def stream_info(self):
        if not self.is_connected:
            self.connect()

        return self._stream_info

    @property
    def chunk_size(self) -> (float, int):
        return self._chunk_size

    @chunk_size.setter
    def chunk_size(self, value: (float, int)):
        self._chunk_size = value

    @property
    def pull_chunks(self) -> bool:
        return self._pull_chunks

    @pull_chunks.setter
    def pull_chunks(self, value: bool):
        self._pull_chunks = value

    def receive_data(self) -> [ndarray, ndarray]:
        if not self.is_connected:
            self.connect()

        return LSLReceiver.get_data_chunk(stream_inlet=self.stream_inlet,
                                          stream_info=self.stream_info,
                                          chunk_size=self.chunk_size,
                                          pull_chunks=self.pull_chunks)

    @property
    def is_connected(self) -> bool:
        return self._stream_inlet is not None

    def connect(self) -> [StreamInlet, dict]:
        """ Connect to LSL stream(s) of device(s)

        :return: pylsl.StreamInlet instance
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
        streams = resolve_stream(stream_type, stream_name)

        # create a new inlet to read from the stream
        stream_inlet = StreamInlet(streams[0])

        stream_meta_data, stream_channels = LSLReceiver.get_lsl_metadata(stream_inlet)

        info = dict(meta_data=stream_meta_data, channels=stream_channels)

        return stream_inlet, info

    @staticmethod
    def get_lsl_metadata(stream_inlet: StreamInlet, ) -> [dict, list]:
        """ getting LSL-stream meta data of an StreamInlet object

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

                stream_channels.append({'label': channel_label, 'type': channel_type, 'unit': channel_unit})
                channels = channels.next_sibling()

        except TypeError:
            pass

        return stream_meta_data, stream_channels

    @staticmethod
    def get_data_chunk(stream_inlet: StreamInlet, stream_info: dict, chunk_size: (float, int),
                       pull_chunks=True) -> [ndarray, ndarray]:

        if isinstance(chunk_size, float):
            chunk_size = int(stream_info['meta_data']['nominal_srate'] * chunk_size)
        assert isinstance(chunk_size, int)

        samples = [] if pull_chunks else empty((chunk_size, stream_info['meta_data']['channel_count']))
        timestamp = [] if pull_chunks else empty(chunk_size)
        sample_count = 0

        if pull_chunks:
            while len(samples) < chunk_size:
                sample, chunk_timestamp = stream_inlet.pull_chunk()

                if len(sample) > 0:
                    samples.extend(sample)
                    timestamp.extend(chunk_timestamp)

        else:
            while sample_count < chunk_size:
                sample, sample_timestamp = stream_inlet.pull_sample()

                samples[sample_count, :] = sample
                timestamp[sample_count] = sample_timestamp
                sample_count += 1

        return asarray(timestamp), asarray(samples)

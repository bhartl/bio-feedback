from biofb.io import Loadable
from biofb.pipeline import Transmitter
from pylsl import StreamOutlet, StreamInfo
from biofb import __manufacturer__ as manufacturer
from collections import defaultdict
from numpy import ndarray, ndim


class LSLTransmitter(Transmitter):
    """ Transmitter class sending data-chunks to the Lab Streaming Layer """

    def __init__(self, stream: str, device: Loadable, channels: (None, [defaultdict]) = None,
                 stream_type: str = 'name', verbose=True, **kwargs):
        Transmitter.__init__(self, stream=stream, device=device, channels=channels,
                             stream_type=stream_type, verbose=verbose, **kwargs)

        self._stream_outlet = None
        self._stream_info = None

        self._init_kwargs = kwargs

    def to_dict(self):
        data = Transmitter.to_dict(self)
        lsl_receiver_data = dict()

        return dict(**data, **lsl_receiver_data)

    @property
    def stream_outlet(self) -> StreamOutlet:
        return self._stream_outlet

    @property
    def stream_info(self):
        return self._stream_info

    @property
    def is_connected(self) -> bool:
        return self._stream_outlet is not None

    def connect(self):
        """ Realize an pylsl StreamOutlet based on the specified device to write data to the LSL

        :return: tuplet of pylsl.StreamOutlet and pylsl.StreamInfo instances
        """

        info = LSLTransmitter.get_lsl_metadata(device=self.device, channels=self.channels)
        stream_outlet = LSLTransmitter.connect_to_lsl_stream(stream_info=info)

        self._stream_outlet = stream_outlet
        self._stream_info = info

        return self.stream_outlet

    def transmit_data(self, data: ndarray):
        """ Put data sample or chunk on the transmission stream

        We here follow closely the
        `pylsl examples/SendData.py <https://github.com/chkothe/pylsl/blob/master/examples/SendData.py>`_
        script.

        :param data: array-like data chunk
        """

        if ndim(data) == 1:
            self._stream_outlet.push_sample(data)
        else:
            self._stream_outlet.push_chunk(data)

        self.augment_sampling_rate()

    @staticmethod
    def connect_to_lsl_stream(stream_info: StreamInfo) -> StreamOutlet:
        """ Create a pylsl.StreamOutlet object based on a StreamInfo instance

        :return: pylsl.StreamOutlet object

        We here follow closely the
        `pylsl examples/HandleMetadata.py <https://github.com/chkothe/pylsl/blob/master/examples/HandleMetadata.py>`_
        script.
        """
        outlet = StreamOutlet(stream_info)
        return outlet

    @staticmethod
    def get_lsl_metadata(device: defaultdict, channels: [defaultdict]) -> StreamInfo:
        """ Create a pylsl.StreamInfo object based on a Device instance

        :return: pylsl.StreamInfo object

        We here follow closely the
        `pylsl examples/HandleMetadata.py <https://github.com/chkothe/pylsl/blob/master/examples/HandleMetadata.py>`_
        script.
        """

        # create a new StreamInfo object which shall describe our stream
        stream_info = StreamInfo(name=device['name'],
                                 type=device['type'],
                                 channel_count=device['channel_count'],
                                 nominal_srate=device['nominal_srate'],
                                 channel_format=device['channel_format'],
                                 source_id=device['source_id']
                                 )

        # now attach some meta-data (in accordance with XDF format, see also code.google.com/p/xdf)
        channels_info = stream_info.desc().append_child("channels")
        for channel in channels:
            # create new xml node
            ch = channels_info.append_child("channel")

            # add xml info
            ch.append_child_value("label", channel['label'])
            ch.append_child_value("type", channel['type'])
            ch.append_child_value("unit", channel['unit'])

        stream_info.desc().append_child_value("manufacturer", manufacturer)

        return stream_info

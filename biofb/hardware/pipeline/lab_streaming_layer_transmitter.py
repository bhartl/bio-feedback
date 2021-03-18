from biofb.io import Loadable
from biofb.hardware import Device
from pylsl import StreamOutlet, StreamInfo
from biofb import __manufacturer__ as manufacturer


class LSLTransmitter(Loadable):
    """ WIP """

    def __init__(self, device: Device, stream: str, stream_type: str = 'name', channel_format='float32', **kwargs):
        Loadable.__init__(self)

        self._device = None
        self.device = device

        self._stream = None
        self.stream = stream

        self._stream_type = None
        self.stream_type = stream_type

        self._stream_outlet = None
        self._stream_info = None

        self._init_kwargs = kwargs

    @property
    def device(self) -> Device:
        return self._device

    @device.setter
    def device(self, value: Device):
        self._device = Device.load(value)

    @property
    def stream(self):
        return self._stream

    @stream.setter
    def stream(self, value):
        self._stream = value

    @property
    def stream_outlet(self):
        return self._stream_outlet

    @property
    def stream_info(self):
        return self._stream_info

    def connect(self):
        """ Realize an pylsl StreamOutlet based on the specified device to write data to the LSL

        :return: tuplet of pylsl.StreamOutlet and pylsl.StreamInfo instances
        """

        info = LSLTransmitter.get_lsl_metadata(self.device)
        stream_outlet = LSLTransmitter.connect_to_lsl_stream(stream_name=self.stream, stream_type=self.stream_type)

        self._stream_outlet = stream_outlet
        self._stream_info = info

        return self.stream_outlet, self._stream_info

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
    def get_lsl_metadata(device: Device, ) -> StreamInfo:
        """ Create a pylsl.StreamInfo object based on a Device instance

        :return: pylsl.StreamInfo object

        We here follow closely the
        `pylsl examples/HandleMetadata.py <https://github.com/chkothe/pylsl/blob/master/examples/HandleMetadata.py>`_
        script.
        """

        # create a new StreamInfo object which shall describe our stream
        stream_info = StreamInfo(name=device.name,
                                 type=device.name,
                                 channel_count=len(device.channels),
                                 nominal_srate=device.sampling_rates[0],
                                 channel_format=device.channels[0].data_format,
                                 source_id=device.name
                                 )

        # now attach some meta-data (in accordance with XDF format, see also code.google.com/p/xdf)
        channels = stream_info.desc().append_child("channels")
        for channel in device.channels:
            ch = channels.append_child("channel")
            ch.append_child_value("name", channel.name)
            ch.append_child_value("label", channel.label)
            ch.append_child_value("unit", channel.unit)
            ch.append_child_value("type", channel.type)

        stream_info.desc().append_child_value("manufacturer", manufacturer)

        return stream_info

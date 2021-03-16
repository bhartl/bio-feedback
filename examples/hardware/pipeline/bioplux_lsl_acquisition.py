""" We here follow closely the `[How-To] <https://biosignalsplux.discussion.community/post/howto-receive-signal-streams-using-opensignals-amp-python-10287105>`_
    Receive Signal Streams using OpenSingals and Python by biosignalsplux.

    See also the documentary `<PROJECT HOME>/doc/bioplux/OpenSignals LSL Manual.pdf`

    Further information is provided on the biosignalsplux `github <https://github.com/biosignalsplux/opensignals-samples/tree/master/LSL>`_

    See also the official
    `example <https://github.com/chkothe/pylsl/blob/master/examples/ReceiveData.py>`_
    to `ReceiveData.py` with `pylsl`.

    There is 3 different options are presented which can be useful for different use cases which are presented below:

    **Option 1**: Resolve stream from an unspecified OpenSignals stream

    This option can be used when only one instance of OpenSignals is being used with no other machines in the network
    using OpenSignals & the LSL module. To resolve the stream, specify the name of the stream using pylsl’s
    resolve_stream function. In the case of OpenSignals, the stream name is set to OpenSignals.

    **Option 2**: Resolve stream from a specific PLUX device via OpenSignals

    This option can be used when multiple devices are being used & you need access to the stream of a specific device,
    you can use the device’s MAC-address to identify the stream. The MAC-address can be found on the back of the device.
    Specify the MAC-address of the device using pylsl’s *resolve_stream* function.

    **Option 3**: Resolve stream data from a specific host machine

    This option can be used when multiple machines in your network are running OpenSignals & you need access to the
    stream of a specific machine. The hostname is the name of the computer streaming the data. Specify the hostname
    of the host machine using pylsl’s resolve_stream function.
"""

from pylsl import StreamInlet
from pylsl import resolve_stream  # The LSL system allows you to receive signal streams using different identifiers of your choice.
import numpy as np


def data_acquisition(stream_inlet, sample_rate=500, chunk_size=1/2, max_steps=10, channels=None):

    print(f'start with data-acquisition for {max_steps} sec.:')

    chunk_size = int(sample_rate*chunk_size)
    data, steps = None, None

    chunk_count = 0
    pull = True
    while pull:
        # get a new sample (you can also omit the timestamp part if you're not interested in it)
        # sample, timestamp = inlet.pull_chunk(max_samples=chunk_size)

        samples = []
        while True:
            sample, timestamp = stream_inlet.pull_sample()
            samples.append(sample)

            if len(samples) >= chunk_size:
                break

        if len(sample) > 0:

            if data is None:
                data = np.asarray(samples)
            else:
                data = np.concatenate([data, samples])

            if steps is None:
                steps = np.arange(0, chunk_size)
            else:
                steps = np.concatenate([steps, np.arange(steps[-1], chunk_size)])

            chunk_count += chunk_size/sample_rate
            pull = chunk_count < max_steps

            print(f"{timestamp} - chunk {chunk_count}: pulled {len(samples)} samples.")
            # print(timestamp, sample)

    import matplotlib.pyplot as plt

    labels = None if channels is None else [f"{l} [{u}]" for l, u in channels]

    plt.plot(data[:, 0], data[:, 1:3], label=labels[1:3])
    plt.legend()
    plt.show()


def get_lsl_metadata(stream_inlet: StreamInlet, ) -> tuple:
    """ getting LSL-stream meta data of an StreamInlet object

    :return: tuple of (meta_data, channels) dictionaries
    """

    stream_meta_data = dict()
    stream_channels = []

    # extract general information about the stream
    stream_info = stream_inlet.info()

    stream_meta_data['name'] = stream_info.name()
    stream_meta_data['mac'] = stream_info.type()
    stream_meta_data['host'] = stream_info.hostname()
    stream_meta_data['channel_count'] = stream_info.channel_count()
    stream_meta_data['channel_format'] = stream_info.channel_format()
    stream_meta_data['sample_rate'] = stream_info.nominal_srate()
    stream_meta_data['source_id'] = stream_info.source_id()
    stream_meta_data['session_id'] = stream_info.session_id()
    stream_meta_data['created_at'] = stream_info.created_at()
    stream_meta_data['version'] = stream_info.version()

    # extract channel specific information of the stream (using the .desc() method on the stream_info object
    channels = stream_info.desc().child("channels").child("channel")

    for i in range(stream_meta_data['channel_count']):  # loop through all available channels
        channel = i + 1  # get the channel number (e.g., 1)
        sensor = channels.child_value("label")   # get the channel type (e.g., ECG, EEG, ...)
        unit = channels.child_value("unit")       # get the channel unit (e.g., mV, ...)
        print(channels)

        stream_channels.append((sensor, unit))
        channels = channels.next_sibling()

    return stream_meta_data, stream_channels


def named_device(stream_name='OpenSignals', chunk_size=1/2, max_steps=10):
    """ Receive data from a list of devices via the Lab Streaming Layer (LSL) using pylsl

    :param stream_name: stream name which are to be acquired by `pylsl``.

    """
    print('bio-feedback example:  Lab Streaming Layer (LSL) data acquisition')

    stream_type = 'name'

    # first resolve an EEG stream on the lab network
    print(f"looking for a stream-{stream_type} `{stream_name}` ...")
    streams = resolve_stream(stream_type, stream_name)

    # create a new inlet to read from the stream
    inlet = StreamInlet(streams[0])

    meta_data, channels = get_lsl_metadata(stream_inlet=inlet)

    for k, v in meta_data.items():
        print(f'{k}:\t{v}')

    for channel_id, channel in enumerate(channels):
        print(f'CH{channel_id} (label / unit):\t{channel}')

    print(f'found stream with {inlet.channel_count} channels with data-format ')
    return data_acquisition(stream_inlet=inlet, sample_rate=meta_data['sample_rate'], chunk_size=chunk_size, max_steps=max_steps, channels=channels)


def specific_device(mac="00:07:80:0F:31:5C", chunk_size=1/2, max_steps=10):
    """ Receive data from a list of devices via the Lab Streaming Layer (LSL) using pylsl

    :param mac: list or tuple of stream names which are to be acquired by `pylsl``.

    """
    print('bio-feedback example:  Lab Streaming Layer (LSL) data acquisition')

    # first resolve an EEG stream on the lab network
    print(f"looking for a device (mac) `{mac}` ...")
    streams = resolve_stream('type', mac)

    # create a new inlet to read from the stream
    inlet = StreamInlet(streams[0])

    meta_data, channels = get_lsl_metadata(stream_inlet=inlet)

    for k, v in meta_data.items():
        print(f'{k}:\t{v}')

    for channel_id in sorted(list(channels.keys())):
        channel = channels[channel_id]
        print(f'CH{channel_id} (label / unit):\t{channel}')

    print(f'found stream with {inlet.channel_count} channels with data-format ')
    return data_acquisition(stream_inlet=inlet, sample_rate=meta_data['sample_rate'], chunk_size=chunk_size, max_steps=max_steps, channels=channels)


def hostname_device(hostname="00:07:80:0F:31:5C", chunk_size=1/2, max_steps=10):
    """ Receive data from a list of devices via the Lab Streaming Layer (LSL) using pylsl

    :param hostname: list or tuple of stream names which are to be acquired by `pylsl``.

    """
    print('bio-feedback example:  Lab Streaming Layer (LSL) data acquisition')

    # first resolve an EEG stream on the lab network
    print(f"looking for a hostname `{hostname}` ...")
    streams = resolve_stream('hostname', hostname)

    # create a new inlet to read from the stream
    inlet = StreamInlet(streams[0])

    meta_data, channels = get_lsl_metadata(stream_inlet=inlet)

    for k, v in meta_data.items():
        print(f'{k}:\t{v}')

    for channel_id in sorted(list(channels.keys())):
        channel = channels[channel_id]
        print(f'CH{channel_id} (label / unit):\t{channel}')

    print(f'found stream with {inlet.channel_count} channels with data-format ')
    return data_acquisition(stream_inlet=inlet, sample_rate=meta_data['sample_rate'], chunk_size=chunk_size, max_steps=max_steps, channels=channels)


if __name__ == '__main__':
    import argh
    argh.dispatch_commands([named_device, specific_device, hostname_device])

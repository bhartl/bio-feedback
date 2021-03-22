""" Receiving single-device data from the Lab-Streaming-Layer using the bio-feedback framework """

from biofb.session import Sample, Subject
from biofb.hardware import Setup
from biofb.hardware import Device
from biofb.pipeline import LSLReceiver
from biofb.visualize import DataMonitor
import numpy as np
import time
import matplotlib.pyplot as plt


TEST_FILE_SAMPLE = 'test/data/session/sample/bioplux_and_unicorn_sample.yml'


def data_slice(plot_data, sample_data, t):
    t_split_interval = None

    if t < len(plot_data):
        t_interval = t + len(sample_data)
    else:
        t_interval = len(sample_data)

    if t_interval >= len(plot_data):
        t_split_interval = t_interval - len(plot_data) + 1
        t_interval = len(plot_data) - 1

    if t_split_interval is not None:
        plot_data[:t_split_interval] = sample_data[-t_split_interval:]
    else:
        t_split_interval = len(sample_data)

    plot_data[t:t_interval] = sample_data[:t_split_interval]

    return plot_data


def device_acquisition(stream='OpenSignals', delta_time=10, total_time=1000, skip_samples=1, ylim=1.5, lw=2.):
    device = Device(name='lsl-receiver')

    receiver_cls = LSLReceiver
    receiver_kwargs = {'stream': stream, 'stream_type': 'name', 'chunk_size': 1/10, 'pull_chunks': True}
    device.receiver = (receiver_cls, receiver_kwargs)

    print('LSL stream infos: ')
    for k, v in device.receiver.stream_info['meta_data'].items():
        print(f'  {k}: {v}')

    print()
    print('LSL channel infos: ')
    for c in device.receiver.stream_info['channels']:
        print(f'  {c}')

    print()
    print('Mapped Channels: ')
    plot_channels = []
    counter_idx = None
    show_idx = []
    for i, c in enumerate(device.channels):
        print(f'  {c}')

        if not any(s in c.name for s in ['nSeq', 'CNT']):
            show_idx.append(i)
            plot_channels.append({'label': f"{c.name} [{c.unit}]", 'lw': lw})

        else:
            counter_idx = i

    plt_kwargs = {
        'xlim': ((0, delta_time * device.receiver.stream_info['meta_data']['nominal_srate']), {}),
        'ylim': ((-abs(ylim), abs(ylim)), {}),
        'xlabel': (('steps',), {}),
        'ylabel': (('sensor data',), {})
    }

    plt.style.use('fivethirtyeight')
    with DataMonitor(channels=plot_channels, plt_kwargs=plt_kwargs, figsize=(10, 5)) as dm:

        steps = None

        for i in range(int(total_time/receiver_kwargs['chunk_size'])):

            # updates device data ...
            time, samples = device.receive_data()

            if counter_idx is None:
                if steps is None:
                    steps = np.arange(0, samples.shape[0])
                else:
                    steps = np.concatenate([steps, np.arange(steps[-1], steps[-1] + samples.shape[0])])

            # here we access the device data
            data_slice = int(delta_time * device.receiver.stream_info['meta_data']['nominal_srate'])

            x = device.data[-data_slice::skip_samples, counter_idx] if counter_idx is not None else steps[-data_slice::skip_samples]
            y = device.data[-data_slice::skip_samples, show_idx]
            plot_data = np.concatenate([x[:, None], y], axis=-1)

            dm.data = plot_data.T

        print("Done with data-acquisition")


def setup_acquisition(stream='OpenSignals', delta_time=10, total_time=1000, skip_samples=1, ylim=1.5, lw=2.):
    device = Device(name='lsl-receiver')
    setup = Setup(name='SoloPlux', devices=[device])

    receiver_cls = LSLReceiver
    receiver_kwargs = {'stream': stream, 'stream_type': 'name', 'chunk_size': 1/10, 'pull_chunks': True}
    device.receiver = (receiver_cls, receiver_kwargs)

    print('LSL stream infos: ')
    for k, v in device.receiver.stream_info['meta_data'].items():
        print(f'  {k}: {v}')

    print()
    print('LSL channel infos: ')
    for c in device.receiver.stream_info['channels']:
        print(f'  {c}')

    print()
    print('Mapped Channels: ')
    plot_channels = []
    counter_idx = None
    show_idx = []
    for i, c in enumerate(device.channels):
        print(f'  {c}')

        if not any(s in c.name for s in ['nSeq', 'CNT']):
            show_idx.append(i)
            plot_channels.append({'label': f"{c.name} [{c.unit}]", 'lw': lw})

        else:
            counter_idx = i
    plt_kwargs = {
        'xlim': ((0, delta_time * device.receiver.stream_info['meta_data']['nominal_srate']), {}),
        'ylim': ((-abs(ylim), abs(ylim)), {}),
        'xlabel': (('steps',), {}),
        'ylabel': (('sensor data',), {})
    }

    plt.style.use('fivethirtyeight')
    with DataMonitor(channels=plot_channels, plt_kwargs=plt_kwargs, figsize=(10, 5)) as dm:

        steps = None

        for i in range(int(total_time/receiver_kwargs['chunk_size'])):

            # updates setup data ...
            time, samples = setup.receive_data()[0]

            if counter_idx is None:
                if steps is None:
                    steps = np.arange(0, samples.shape[0])
                else:
                    steps = np.concatenate([steps, np.arange(steps[-1], steps[-1] + samples.shape[0])])

            # here we access setup data
            data_slice = int(delta_time * device.receiver.stream_info['meta_data']['nominal_srate'])

            x = setup.data[0][-data_slice::skip_samples, counter_idx] if counter_idx is not None else steps[-data_slice::skip_samples]
            y = setup.data[0][-data_slice::skip_samples, show_idx]
            plot_data = np.concatenate([x[:, None], y], axis=-1)

            dm.data = plot_data.T

            # device data is not set
            assert device._data is None

        print("Done with data-acquisition")


def sample_acquisition(stream='OpenSignals', delta_time=10, total_time=1000, skip_samples=1, ylim=1.5, lw=2.):
    device = Device(name='lsl-receiver')
    setup = Setup(name='SoloPlux', devices=[device])
    sample = Sample(setup=setup, subject=Subject(identity='id'))

    receiver_cls = LSLReceiver
    receiver_kwargs = {'stream': stream, 'stream_type': 'name', 'chunk_size': 1/10, 'pull_chunks': True}
    device.receiver = (receiver_cls, receiver_kwargs)

    print('LSL stream infos: ')
    for k, v in device.receiver.stream_info['meta_data'].items():
        print(f'  {k}: {v}')

    print()
    print('LSL channel infos: ')
    for c in device.receiver.stream_info['channels']:
        print(f'  {c}')

    print()
    print('Mapped Channels: ')
    plot_channels = []
    counter_idx = None
    show_idx = []
    for i, c in enumerate(device.channels):
        print(f'  {c}')

        if not any(s in c.name for s in ['nSeq', 'CNT']):
            show_idx.append(i)
            plot_channels.append({'label': f"{c.name} [{c.unit}]", 'lw': lw})

        else:
            counter_idx = i

    plt_kwargs = {
        'xlim': ((0, delta_time * device.receiver.stream_info['meta_data']['nominal_srate']), {}),
        'ylim': ((-abs(ylim), abs(ylim)), {}),
        'xlabel': (('steps',), {}),
        'ylabel': (('sensor data',), {})
    }

    plt.style.use('fivethirtyeight')
    with DataMonitor(channels=plot_channels, plt_kwargs=plt_kwargs, figsize=(10, 5)) as dm:

        steps = None

        for i in range(int(total_time/receiver_kwargs['chunk_size'])):

            # updates sapmle data ... we get a list of samples, one batch for each device
            samples = sample.state

            # we only have one device specified
            samples = samples[0]

            if counter_idx is None:
                if steps is None:
                    steps = np.arange(0, samples.shape[0])
                else:
                    steps = np.concatenate([steps, np.arange(steps[-1], steps[-1] + samples.shape[0])])

            # here we acess sample data
            data_slice = int(delta_time * device.receiver.stream_info['meta_data']['nominal_srate'])

            x = sample.data[0][-data_slice::skip_samples, counter_idx] if counter_idx is not None else steps[-data_slice::skip_samples]
            y = sample.data[0][-data_slice::skip_samples, show_idx]
            plot_data = np.concatenate([x[:, None], y], axis=-1)

            dm.data = plot_data.T

            # neither the setup nor the device data are set
            assert device._data is None
            assert setup._data is None

        print("Done with data-acquisition")


def acquire_sample_data(streams=['Bioplux', 'Unicorn'], chunk_size=1., verbose=True,
                        delta_time=10, total_time=1000, lw=2., ylim=2.):

    hardware_setup = Setup.from_streams(
        name='LSL Streaming Setup',
        receiver_cls=LSLReceiver,
        streams=streams,
        stream_kwargs=dict(chunk_size=chunk_size,
                           verbose=verbose,
                           ),
    )

    try:
        # receive data
        then = time.time()
        for i in range(10):
            timestamps, samples = hardware_setup.receive_data()

            now = time.time()
            print(f'received {[len(data) for data in samples]} data-points from {hardware_setup.n_devices} devices after {now-then:.2f} sec.')
            then = now

    finally:
        hardware_setup.stop()

    print("Done with data-acquisition")

    from multiprocessing import Process

    device_plot = [
        Process(target=device.plot)
        for device in hardware_setup.devices
    ]

    [dp.start() for dp in device_plot]
    [dp.join() for dp in device_plot]

    exit()

if __name__ == '__main__':
    import argh
    argh.dispatch_commands([device_acquisition, setup_acquisition, sample_acquisition, acquire_sample_data])

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


def device_acquisition(stream='OpenSignals', delta_time=10, total_time=1000, skip_samples=1, ylim=1.5, lw=2.):
    """ Receive data from specified stream and update a biofb.hardware.Device data array

    :param stream: LSL stream name
    :param delta_time: Time-interval in seconds which is shown (data plotting is dynamical)
    :param total_time: Total time in seconds in which data is received
    :param skip_samples: Integer interval controlling, how many data skipped when plotting (i.e., skip_samples-1),
                         defaults to 1.
    :param ylim: Numerical range of the y-axis, defaults to 1.5
    :param lw: linewidht, defaults to 2
    """

    # create device instance
    device = Device(name='lsl-receiver')

    # create and associate LSLReceiver to device
    receiver_cls = LSLReceiver
    receiver_kwargs = {'stream': stream, 'stream_type': 'name', 'chunk_size': 1/10, 'pull_chunks': True}
    device.receiver = (receiver_cls, receiver_kwargs)

    # print stream infos
    print('LSL stream infos: ')
    for k, v in device.receiver.stream_info['meta_data'].items():
        print(f'  {k}: {v}')

    # print channel infos
    print()
    print('LSL channel infos: ')
    for c in device.receiver.stream_info['channels']:
        print(f'  {c}')

    # print channel mapping (don't show nSeq or CNT channels but use them as x-axis array)
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

    # specify matplotlib plt formatting
    plt_kwargs = {
        'xlim': ((0, delta_time * device.receiver.stream_info['meta_data']['nominal_srate']), {}),
        'ylim': ((-abs(ylim), abs(ylim)), {}),
        'xlabel': (('steps',), {}),
        'ylabel': (('sensor data',), {})
    }

    with DataMonitor(channels=plot_channels,
                     ax_kwargs=plt_kwargs,
                     make_fig_kwargs=dict(figsize=(10, 5)),
                     ) as dm:

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

    with DataMonitor(channels=plot_channels,
                     ax_kwargs=plt_kwargs,
                     make_fig_kwargs=dict(figsize=(10, 5)),
                     ) as dm:

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

    with DataMonitor(channels=plot_channels,
                     ax_kwargs=plt_kwargs,
                     make_fig_kwargs=dict(figsize=(10, 5)),
                     ) as dm:

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


def multiple_device_acquisition(streams=['Bioplux', 'Unicorn'], chunk_size=1./5., verbose=True,
                                delta_time=10, total_time=15., lw=2., ylim=4.):

    # try to load hardware setup based on lab-streaming-layer meta-information
    hws = Setup.from_streams(
        name='LSL Streaming Setup',
        receiver_cls=LSLReceiver,
        streams=streams,
        stream_kwargs=dict(chunk_size=chunk_size,
                           pull_chunks=True,
                           verbose=verbose,
                           ),
    )

    data_slices = [int(delta_time * device.sampling_rate) for device in hws]

    def make_figure(**kwargs):
        f, axes = plt.subplots(hws.n_devices, 1, **kwargs)
        return f, axes

    def ax_plot(ax, data, channels):
        for device_ax, device_data, device_channels, dt_slice in zip(ax, data, channels, data_slices):
            for y, c in zip(device_data, device_channels):
                device_ax.plot(y[-dt_slice::], **c)

    plot_channels = [
        [dict(label=c.label, lw=lw) for c in d.channels]
        for d in hws.devices
    ]

    plt_kwargs = [
        {'set_xlim': ((0, delta_time * device.sampling_rate), {}),
         'set_ylim': ((-abs(ylim), abs(ylim)), {}),
         'set_xlabel': (('steps' if (i == (hws.n_devices - 1)) else None, ), {}),
         'set_ylabel': ((device.name,), {})}
        for i, device in enumerate(hws.devices)
    ]

    try:
        with DataMonitor(channels=plot_channels,
                         ax_kwargs=plt_kwargs,
                         make_fig=make_figure,
                         ax_plot=ax_plot,
                         make_fig_kwargs=dict(figsize=(15, 5)),
                         style=None,
                         ) as dm:

            # receive data
            then = time.time()
            n_chunks = int(total_time/chunk_size)
            for i in range(n_chunks):
                # list of (timestamps, samples)-tuples for each device
                multidevice_data = hws.receive_data()
                dm.data = [d.T for d in hws.data]

                now = time.time()
                print(f'received chunk {i}/{n_chunks} with {[len(samples) for timestamps, samples in multidevice_data]} data-points from {hws.n_devices} devices after {now-then:.2f} sec.')
                then = now

            print("Done with data-acquisition, cleaning up ...")

            print("Plot collected data using device-plot functions")
            from multiprocessing import Process

            device_plot = [
                Process(target=device.plot)
                for device in hws.devices
            ]

            [dp.start() for dp in device_plot]
            [dp.join() for dp in device_plot]

    finally:
        hws.stop()

    print('Done')
    exit()


if __name__ == '__main__':
    import argh
    argh.dispatch_commands([device_acquisition,
                            setup_acquisition,
                            sample_acquisition,
                            multiple_device_acquisition,
                            ])

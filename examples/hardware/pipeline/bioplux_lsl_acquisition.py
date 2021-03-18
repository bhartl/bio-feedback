from biofb.session import Sample, Subject
from biofb.hardware import Setup
from biofb.hardware.devices import Bioplux
from biofb.hardware.pipeline import LSLReceiver
from biofb.signal.visualize import DataMonitor


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


def device_acquisition(delta_time=10, total_time=1000, skip_samples=1, ylim=1.5):
    bp = Bioplux(name='bioplux-receiver')

    receiver_cls = LSLReceiver
    receiver_kwargs = {'stream': 'OpenSignals', 'stream_type': 'name', 'chunk_size': 1/10, 'pull_chunks': True}
    bp.receiver = (receiver_cls, receiver_kwargs)

    print('LSL stream infos: ')
    for k, v in bp.receiver.stream_info['meta_data'].items():
        print(f'  {k}: {v}')

    print()
    print('LSL channel infos: ')
    for c in bp.receiver.stream_info['channels']:
        print(f'  {c}')

    print()
    print('Mapped Channels: ')
    plot_channels = []
    for i, c in enumerate(bp.channels):
        print(f'  {c}')

        if i > 0:
            plot_channels.append({'label': f"{c.name} [{c.unit}]"})

    plt_kwargs = {
        'xlim': ((0, delta_time * bp.receiver.stream_info['meta_data']['sampling_rate']), {}),
        'ylim': ((-abs(ylim), abs(ylim)), {}),
        'xlabel': (('steps',), {}),
        'ylabel': (('sensor data',), {})
    }

    with DataMonitor(channels=plot_channels, plt_kwargs=plt_kwargs, figsize=(10, 5)) as dm:

        for i in range(int(total_time/receiver_kwargs['chunk_size'])):

            # updates device data ...
            time, samples = bp.receive_data()

            # here we access the device data
            data_slice = int(delta_time * bp.receiver.stream_info['meta_data']['sampling_rate'])
            dm.data = bp.data[-data_slice::skip_samples, :].T

        print("Done with data-acquisition")


def setup_acquisition(delta_time=10, total_time=1000, skip_samples=1, ylim=1.5):
    bp = Bioplux(name='bioplux-receiver')
    setup = Setup(name='SoloPlux', devices=[bp])

    receiver_cls = LSLReceiver
    receiver_kwargs = {'stream': 'OpenSignals', 'stream_type': 'name', 'chunk_size': 1/10, 'pull_chunks': True}
    bp.receiver = (receiver_cls, receiver_kwargs)

    print('LSL stream infos: ')
    for k, v in bp.receiver.stream_info['meta_data'].items():
        print(f'  {k}: {v}')

    print()
    print('LSL channel infos: ')
    for c in bp.receiver.stream_info['channels']:
        print(f'  {c}')

    print()
    print('Mapped Channels: ')
    plot_channels = []
    for i, c in enumerate(bp.channels):
        print(f'  {c}')

        if i > 0:
            plot_channels.append({'label': f"{c.name} [{c.unit}]"})

    plt_kwargs = {
        'xlim': ((0, delta_time * bp.receiver.stream_info['meta_data']['sampling_rate']), {}),
        'ylim': ((-abs(ylim), abs(ylim)), {}),
        'xlabel': (('steps',), {}),
        'ylabel': (('sensor data',), {})
    }

    with DataMonitor(channels=plot_channels, plt_kwargs=plt_kwargs, figsize=(10, 5)) as dm:

        for i in range(int(total_time/receiver_kwargs['chunk_size'])):

            # updates setup data ...
            time, samples = setup.receive_data()[0]

            # here we access setup data
            data_slice = int(delta_time * bp.receiver.stream_info['meta_data']['sampling_rate'])
            dm.data = setup.data[0][-data_slice::skip_samples].T

            # device data is not set
            assert bp._data is None

        print("Done with data-acquisition")


def sample_acquisition(delta_time=10, total_time=1000, skip_samples=1, ylim=1.5):
    bp = Bioplux(name='bioplux-receiver')
    setup = Setup(name='SoloPlux', devices=[bp])
    sample = Sample(setup=setup, subject=Subject(identity='id'))

    receiver_cls = LSLReceiver
    receiver_kwargs = {'stream': 'OpenSignals', 'stream_type': 'name', 'chunk_size': 1/10, 'pull_chunks': True}
    bp.receiver = (receiver_cls, receiver_kwargs)

    print('LSL stream infos: ')
    for k, v in bp.receiver.stream_info['meta_data'].items():
        print(f'  {k}: {v}')

    print()
    print('LSL channel infos: ')
    for c in bp.receiver.stream_info['channels']:
        print(f'  {c}')

    print()
    print('Mapped Channels: ')
    plot_channels = []
    for i, c in enumerate(bp.channels):
        print(f'  {c}')

        if i > 0:
            plot_channels.append({'label': f"{c.name} [{c.unit}]"})

    plt_kwargs = {
        'xlim': ((0, delta_time * bp.receiver.stream_info['meta_data']['sampling_rate']), {}),
        'ylim': ((-abs(ylim), abs(ylim)), {}),
        'xlabel': (('steps',), {}),
        'ylabel': (('sensor data',), {})
    }

    with DataMonitor(channels=plot_channels, plt_kwargs=plt_kwargs, figsize=(10, 5)) as dm:

        for i in range(int(total_time/receiver_kwargs['chunk_size'])):

            # updates sapmle data ...
            samples = sample.state

            # here we acess sample data
            data_slice = int(delta_time * bp.receiver.stream_info['meta_data']['sampling_rate'])
            dm.data = sample.data[0][-data_slice::skip_samples].T

            # neither the setup nor the device data are set
            assert bp._data is None
            assert setup._data is None

        print("Done with data-acquisition")


if __name__ == '__main__':
    import argh
    argh.dispatch_commands([device_acquisition, setup_acquisition, sample_acquisition])

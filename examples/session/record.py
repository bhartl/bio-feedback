from biofb.controller.audio import AudioKeySession
from biofb.controller import Agent, KeyAgent
from biofb.visualize import DataMonitor
from examples.session.configure import *


def monitor_session(session, delta_time=5., lw=2., ):

    from examples.session.monitor import make_figure, ax_plot, ax_legend

    hws = session.sample.setup
    data_slices = [int(delta_time * device.sampling_rate) for device in hws]

    plot_channels = [
        [dict(label=c.name, lw=lw, dt_slice=ds)
         for c in d.channels
         ]
        for d, ds in zip(hws.devices, data_slices)
    ]

    n_channels = 9
    plt_kwargs = []
    for i_channel in range(n_channels):

        device_kwargs = []
        for i, device in enumerate(hws.devices):
            device_channel_kwargs = {
                'set_xlim': ((0, delta_time * device.sampling_rate), {}),
                # 'set_ylim': ((-abs(ylim), abs(ylim)), {}),
            }

            if i_channel == 0:
                device_channel_kwargs['set_title'] = ((device.name,), {})

            if i_channel == n_channels - 1:
                device_channel_kwargs['set_xlabel'] = (('steps',), {})

            else:
                device_channel_kwargs['set_xticklabels'] = (([],), {})

            device_kwargs.append(device_channel_kwargs)

        plt_kwargs.append(device_kwargs)

    dm = DataMonitor(channels=plot_channels,
                     ax_kwargs=plt_kwargs,
                     make_fig=make_figure,
                     ax_plot=ax_plot,
                     make_fig_kwargs=dict(figsize=(15, 10), n_devices=hws.n_devices, n_channels=n_channels),
                     legend=ax_legend,
                     style=None,
                     )

    try:
        dm.start()
        session.run(data_monitor=dm)
        print('Session stopped, wait for monitor to close.')

    finally:
        session.stop()
        dm.stop()


def perform_session(sample_path_pattern, setting, setup, subject, monitor_kwargs=()):

    sample = new_sample(sample_path_pattern=sample_path_pattern,
                        setting=setting,
                        setup=setup,
                        subject=subject)

    _ = sample.state

    controller = setting.controller

    if not isinstance(controller, Agent):
        agent = KeyAgent(
            name='session_agent',
            description='tracks start and stop of a session',
            keymap_action={'Key.esc': -1, '.': 0},
            verbose=False,
        )
    else:
        agent = controller

    session = AudioKeySession(sample=sample,
                              agent=agent,
                              name='biofb session',
                              description='',
                              action_successive=False,  # allow to stop action
                              delay=0.
                              )

    try:
        print(session.agent)
        monitor_session(session=session, **dict(monitor_kwargs))
    except KeyboardInterrupt:
        print('Detected Keyboard interrupt.')
        save_data = input('Do you still want to save the data? (press y to save): y').strip().lower()
        if save_data in ('n', 'no'):
            raise

    return session


def main(sample_path_pattern='data/session/biofb/recording-<ACQUISITION_DATETIME>.h5',
         streams=DEFAULT_STREAMS,
         chunk_size: float = 1.,
         delta_time: float = 15.,
         known_settings: str = KNOWN_SETTINGS,
         known_locations: str = KNOWN_LOCATIONS,
         known_controllers: str = KNOWN_CONTROLLERS,
         known_subjects: str = KNOWN_SUBJECTS,
         quiet: bool = False,
         ):
    """ Perform a `biofb.controller.audio.AudioKeySession`

    :param sample_path_pattern: Export-path pattern (use capitalized biofb.session.Sample in `<` and `>` parenthesis
                                such as `<ACQUISITION_DATETIME>`, to replace with property values in the output
                                filename).
    :param streams: Names of the Lab Streaming Layer Streams of the different devices.
    :param chunk_size: Fraction of a the streams sampling rate (if chunk_size is float) or the number of
                       data-samples (if chunk_size is int) which are considered a chunk of samples
                       (defaults to 1., i.e. 1-sek chunks are received from the hardware. should not be too small,
                       otherwise the latency is too high).
    :param delta_time: Time-window in seconds for which the data of the session are shown.
    :param quiet: Defaults to False, i.e. verbose operation.
    :param known_settings: path to KNOWN_SETTINGS csv file (defaults to data/session/db_meta_data/session.csv).
    :param known_locations: path to KNOWN_LOCATIONS csv file (defaults to data/session/db_meta_data/location.csv).
    :param known_controllers: path to KNOWN_CONTROLLERS csv file (defaults to data/session/db_meta_data/controller.csv).
    :param known_subjects: path to KNOWN_SUBJECTS csv file (defaults to data/session/db_meta_data/subject.csv).
    """

    print('BIOFB SESSION RECORDER ... (c) by Brain Project')
    print()

    print('---')
    print('1.) Specify the session setting')
    print('2.) Specify the session participant')
    print('3.) Specify the hardware setup data streams')
    print('4.) Start the session')
    print('5.) Perform your experiments')
    print('6.) End the session, add sample comments and store the acquired data')
    print('---')
    print()

    print('---')
    setting, setting_id = select_setting(known_settings=known_settings,
                                         known_locations=known_locations,
                                         known_controllers=known_controllers,
                                         )
    print('chosen setting: ', setting)
    print('---')
    print()

    print('---')
    subject, subject_id = select_subject(known_subjects=known_subjects)
    print('chosen participant: ', subject)
    print('---')
    print()

    print('---')
    export_path = input(f'chosen Sample export-pattern ({sample_path_pattern}): ').strip()
    if export_path == "":
        export_path = sample_path_pattern
    sample_path_pattern = export_path
    print('---')
    print()

    print('---')
    hardware_setup = connect_to_devices(streams=streams, chunk_size=chunk_size, verbose=not quiet)
    print('---')
    print()

    print('---')
    session = perform_session(sample_path_pattern=sample_path_pattern,
                              setting=setting,
                              subject=subject,
                              setup=hardware_setup,
                              monitor_kwargs={'delta_time': delta_time}
                              )
    print('---')
    print()

    print('---')
    comment_sample(session.sample)
    print('---')
    print()

    session.dump()
    exit()


if __name__ == '__main__':
    import argh
    argh.dispatch_command(main)


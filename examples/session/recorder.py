import os
import pandas as pd
from biofb.hardware import Setup
from biofb.session import Subject, Location, Setting, Sample, Controller
from biofb.pipeline import LSLReceiver
from biofb.visualize import DataMonitor
from biofb.controller import Agent, KeyAgent
from biofb.controller import AudioKeySession
import matplotlib.pyplot as plt


KNOWN_CONTROLLERS = "data/session/db_meta_data/controller.csv"
KNOWN_SUBJECTS = "data/session/db_meta_data/subject.csv"
KNOWN_LOCATIONS = "data/session/db_meta_data/location.csv"
KNOWN_SETTINGS = "data/session/db_meta_data/setting.csv"

DEFAULT_STREAMS = ('OpenSignals', 'Unicorn')


def new_loadable(loadable, path, loaded):

    print(f'NEW {loadable.__name__.upper()} MENU')

    new = loadable.from_terminal()
    try:
        loaded = loaded.append(new.to_dict())
    except AttributeError:
        loaded = pd.DataFrame([new.to_dict()])

    if os.path.isfile(path) or isinstance(path, str):
        loaded.to_csv(path, index=False)
        print(f'exported new {loadable.__name__}-DB to file `{path}`')

    new_id = len(loaded) - 1

    return new, new_id


def select_location(known_locations=KNOWN_LOCATIONS):

    print('SELECT LOCATION MENU')

    try:
        locations = Location.load_dict_like(known_locations)
        locations_df = pd.DataFrame(locations)
    except AssertionError:
        locations_df = None

    chosen_id = 'new'
    if locations_df is not None:
        print('Available locations')
        print(locations_df)
        print()
        chosen_id = input(f'Choose from id {locations_df.index.min()} to {locations_df.index.max()} (`n` for new): ')
    else:
        print(f'Enter new location')

    if chosen_id.lower().strip() in ('n', 'new'):
        location, chosen_id = new_loadable(loadable=Location, path=known_locations, loaded=locations_df)

    else:
        location = locations_df.iloc[int(chosen_id.lower().strip())]
        location = Location.load(location.to_dict())

    return location, chosen_id


def select_subject(known_subjects=KNOWN_SUBJECTS):

    print('SELECT SUBJECT MENU')

    try:
        subjects = Subject.load_dict_like(known_subjects)
        subjects_df = pd.DataFrame(subjects)
    except AssertionError:
        subjects_df = None

    chosen_id = 'new'
    if subjects_df is not None:
        print('Available subjects (participants)')
        print(subjects_df[['identity', 'gender', 'year_of_birth']])
        print()
        chosen_id = input(f'Choose from id {subjects_df.index.min()} to {subjects_df.index.max()} (`n` for new): ')
    else:
        print(f'Enter new subject')

    if chosen_id.lower().strip() in ('n', 'new'):
        subject, chosen_id = new_loadable(loadable=Subject, path=known_subjects, loaded=subjects_df)
    else:
        subject = subjects_df.iloc[int(chosen_id.lower().strip())]
        subject = Subject.load(subject.to_dict())

    return subject, chosen_id


def select_controller(known_controllers=KNOWN_CONTROLLERS):

    print('SELECT CONTROLLER MENU')

    try:
        controllers = Controller.load_dict_like(known_controllers)
        controllers_df = pd.DataFrame(controllers)
    except AssertionError:
        controllers_df = None

    assert controllers_df is not None, "Ask you admin to setup a controller configuration."

    print('Available controllers')
    print(controllers_df[['name', 'description']])
    print()
    chosen_id = input(f'Choose from id {controllers_df.index.min()} to {controllers_df.index.max()}: ')

    controller = controllers_df.iloc[int(chosen_id.lower().strip())]
    controller = Controller.load(controller.to_dict())

    return controller, chosen_id


def new_setting(path, loaded,
                known_controllers=KNOWN_CONTROLLERS, known_locations=KNOWN_LOCATIONS):

    print('NEW SETTING MENU')

    name = input('setting name: ')
    description = input('setting description: ')
    print()

    controller, controller_id = select_controller(known_controllers=known_controllers)
    print('chosen controller: ', controller)
    print()

    location, location_id = select_location(known_locations=known_locations)
    print('chosen location: ', location)
    print()

    setting = Setting(name=name,
                      controller=controller,
                      location=location,
                      description=description)

    setting_dict = setting.to_dict()
    setting_dict['controller'] = (known_controllers, controller_id)
    setting_dict['location'] = (known_locations, location_id)

    try:
        loaded = loaded.append(setting_dict, ignore_index=True)
        loaded = loaded.reset_index(drop=True)
    except AttributeError:
        loaded = pd.DataFrame([setting_dict])

    if os.path.isfile(path) or isinstance(path, str):
        loaded.to_csv(path, index=False)
        print(f'exported new Setting-DB to file `{path}`')

    setting_id = len(loaded) - 1

    return setting, setting_id


def select_setting(known_settings=KNOWN_SETTINGS,
                   known_controllers=KNOWN_CONTROLLERS,
                   known_locations=KNOWN_LOCATIONS,
                   ):

    print('SELECT SETTING MENU')

    try:
        settings = Setting.load_dict_like(known_settings)
        settings_df = pd.DataFrame(settings)
    except AssertionError as s:
        settings_df = None

    chosen_id = 'new'
    if settings_df is not None:
        print('Available settings')
        print(settings_df[['name', 'description']])
        print()
        chosen_id = input(f'Choose from id {settings_df.index.min()} to {settings_df.index.max()} (`n` for new): ')
    else:
        print(f'Enter new setting')

    if chosen_id.lower().strip() in ('n', 'new'):
        print()
        setting, chosen_id = new_setting(path=known_settings,
                                         loaded=settings_df,
                                         known_controllers=known_controllers,
                                         known_locations=known_locations,
                                         )

    else:
        setting = settings_df.iloc[int(chosen_id.lower().strip())]
        setting = Setting.load(setting.to_dict())

    return setting, chosen_id


def connect_to_devices(streams=DEFAULT_STREAMS, chunk_size=1./5., verbose=True, ):

    print('DATA STREAM CONNECTION MENU')

    connect_to_streams = input(f'Connect to LSL streams {streams}? (`y/n`, defaults to `y`): ')

    if connect_to_streams.lower().strip() not in ("yes", "y", "j", "ja", ""):
        streams = []
        print('Specify LSL stream (confirm each stream with `return`, enter `done` or blank if finished):')
        while True:
            stream = input('LSL stream: ')
            if stream.lower().strip() in ('done', "'done'", '"done"', '`done`', ""):
                break
            streams.append(stream)

        return connect_to_devices(streams=streams, chunk_size=chunk_size, verbose=verbose)

    # try to load hardware setup based on lab-streaming-layer meta-information
    stream_kwargs = dict(chunk_size=chunk_size,
                         pull_chunks=False,
                         verbose=verbose,
                         )

    hardware_setup = Setup.from_streams(
        name='LSL Streaming Setup',
        receiver_cls=LSLReceiver,
        streams=streams,
        stream_kwargs=stream_kwargs
    )

    print('Connected.')

    return hardware_setup


def new_sample(sample_path_pattern, setting, setup, subject):
    sample = Sample(
        setting=setting,
        subject=subject,
        setup=setup,
        filename=sample_path_pattern.strip()
    )

    return sample


def comment_sample(sample):
    print('SAMPLE COMMENTS MENU')

    comments = sample.comments

    while True:
        comment = input('add sample comment: ').strip()

        if comment == "":
            break

        comments.append(comment)

    sample.comments = comments
    return comments


def safe_run_session(session, **kwargs):
    try:
        print(session.agent)
        session.run(**kwargs)
    finally:
        session.stop()

    return session


def make_figure(n_devices=1, n_channels=8, **kwargs):
    """ helper figure generation-function for custom DataMonitor below (one axis for each device)

    :param n_devices: number of devices whose data are plotted
    :param n_channels: number of devices whose data are plotted
    :param kwargs: keyword arguments passed to plt.subplots method
                   that generates the (fig, axes) matplotlib environment
    """
    f, axes = plt.subplots(n_channels, n_devices, **kwargs)
    return f, axes


def ax_plot(ax, data, channels):
    """ helper plot-function for custom DataMonitor below:
        all device-specific data is plotted in one device-specific axis

    :param ax: matplotlib axes array (here 1D) containing an axes per device
    :param data: list of data for each device, each device-data is a (n_samples x n_channels) array.
    :param channels: list of [channel-information] for each device,
                     each device specific channel-information is a list of [device-channel-info] dict.
                     Each channel specific device-channel-info dict contains
                     (i) key-value_dict pairs that are forwarded to the ax.plot function for each channel-data and
                     (ii) an element 'dt_slice', specifying the number of data that are shown, `data[-dt_slice:]`
    """
    for device_ax, device_data, device_channels in zip(ax.T, data, channels):
        for y, c, ax in zip(device_data, device_channels, device_ax):
            dt_slice = c.pop('dt_slice', len(y))
            ax.plot(y[-dt_slice::], **c)
            ax.set_ylabel(c.get('label', 'sensor'))
            c['dt_slice'] = dt_slice


def ax_legend(ax, channels):
    # [device_ax.legend(loc='center right') for device_ax in ax]
    pass


def monitor_session(session, delta_time=5., lw=2., ):

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

    with DataMonitor(channels=plot_channels,
                     ax_kwargs=plt_kwargs,
                     make_fig=make_figure,
                     ax_plot=ax_plot,
                     make_fig_kwargs=dict(figsize=(10, 8), n_devices=hws.n_devices, n_channels=n_channels),
                     legend=ax_legend,
                     style=None,
                     ) as dm:

        safe_run_session(session=session, data_monitor=dm)

        print('Session stopped, wait for monitor to close.')


def perform_session(sample_path_pattern, setting, setup, subject, monitor_kwargs=(), monitor=False):

    sample = new_sample(sample_path_pattern=sample_path_pattern,
                        setting=setting,
                        setup=setup,
                        subject=subject,
                        )

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
        if monitor:
            monitor_session(session=session, **dict(monitor_kwargs))
        else:
            safe_run_session(session=session)

    except Exception as ex:
        print(f'Detected {ex.__class__.__name__}:', str(ex))
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
         monitor: bool = False,
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
                       [Note: The chunk size can be reduced if a monitor update rate is introduced and specified
                       large enough.]
    :param delta_time: Time-window in seconds for which the data of the session are shown.
    :param quiet: Boolean defining whether the recorder is executed in verbose mode.
    :param quiet: Boolean defining whether signals should be monitored on the screen (defaults to False).
                  If the monitor is activated (True) data will shown in a data-monitor Thread -- make sure you
                  end the data-acquisition before closing the monitor window!
    :param known_settings: path to KNOWN_SETTINGS csv file (defaults to data/session/db_meta_data/session.csv).
    :param known_locations: path to KNOWN_LOCATIONS csv file (defaults to data/session/db_meta_data/location.csv).
    :param known_controllers: path to KNOWN_CONTROLLERS csv file (defaults to data/session/db_meta_data/controller.csv).
    :param known_subjects: path to KNOWN_SUBJECTS csv file (defaults to data/session/db_meta_data/subject.csv).
    """

    print('biofb SESSION RECORDER ... (c) by Brain Project')
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
                              monitor_kwargs={'delta_time': delta_time},
                              monitor=monitor
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


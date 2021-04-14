from biofb.hardware import Setup
from biofb.session import Subject, Location, Setting, Sample, Controller
from biofb.pipeline import LSLReceiver
import os
import pandas as pd
import time

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

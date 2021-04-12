from biofb.hardware import Setup
from biofb.session import Subject, Location, Setting, Sample, Controller
from biofb.controller import KeyAgent
from biofb.pipeline import LSLReceiver
import os
import pandas


def select_location(known_locations="data/session/db_meta_data/location.csv"):

    try:
        locations = Location.load_dict_like(known_locations)
        locations_df = pandas.DataFrame(locations)
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
        location = Location.from_terminal()
        try:
            locations_df = locations_df.append(location.to_dict())
        except AttributeError:
            locations_df = pandas.DataFrame([location.to_dict()])

        if os.path.isfile(known_locations) or isinstance(known_locations, str):
            locations_df.to_csv(known_locations, index=False)
            print(f'exported new locations DB to file `{known_locations}`')

    else:
        location = locations_df.iloc[int(chosen_id.lower().strip())]
        location = Location.load(location.to_dict())

    return location


def select_subject(known_subjects="data/session/db_meta_data/subject.csv"):

    try:
        subjects = Subject.load_dict_like(known_subjects)
        subjects_df = pandas.DataFrame(subjects)
    except AssertionError:
        subjects_df = None

    chosen_id = 'new'
    if subjects_df is not None:
        print('Available subjects (participants)')
        print(subjects_df)
        print()
        chosen_id = input(f'Choose from id {subjects_df.index.min()} to {subjects_df.index.max()} (`n` for new): ')
    else:
        print(f'Enter new subject')

    if chosen_id.lower().strip() in ('n', 'new'):
        subject = Subject.from_terminal()
        try:
            subjects_df = subjects_df.append(subject.to_dict())
        except AttributeError:
            subjects_df = pandas.DataFrame([subject.to_dict()])

        if os.path.isfile(known_subjects) or isinstance(known_subjects, str):
            subjects_df.to_csv(known_subjects, index=False)
            print(f'exported new subjects DB to file `{known_subjects}`')

    else:
        subject = subjects_df.iloc[int(chosen_id.lower().strip())]
        subject = Subject.load(subject.to_dict())

    return subject


def connect_to_devices(streams=('Bioplux', 'Unicorn'), chunk_size=1./5., verbose=True, ):

    print()
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
                         pull_chunks=True,
                         verbose=verbose,
                         )

    hardware_setup = Setup.from_streams(
        name='LSL Streaming Setup',
        receiver_cls=LSLReceiver,
        streams=streams,
        stream_kwargs=stream_kwargs
    )

    return hardware_setup


def main(streams=('Bioplux', 'Unicorn'),
         chunk_size=1.,
         verbose=True
         ):

    print('---')
    location = select_location()
    print('chosen location: ', location)
    print()

    print('---')
    subject = select_subject()
    print('chosen subject: ', subject)
    print('---')
    print()

    print('---')
    hardware_setup = connect_to_devices(streams=streams, chunk_size=chunk_size, verbose=verbose)
    print('---')
    print()


if __name__ == '__main__':
    import argh
    argh.dispatch_command(main)

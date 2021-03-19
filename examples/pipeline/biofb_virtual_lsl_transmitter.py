from biofb.pipeline import LSLTransmitter
from biofb.hardware.devices import Bioplux
from biofb.session import Sample

STREAM_NAME_BIOPLUX = 'VirtualPlux'
TEST_FILE_BIOPLUX = 'test/data/session/sample/bioplux/opensignals_0007800f315c_2021-01-19_15-03-08_converted.txt'
TEST_FILE_SAMPLE = 'test/data/session/sample/bioplux_and_unicorn_sample.yml'


def bioplux_run_start_stop(bioplux_datafile=TEST_FILE_BIOPLUX, **bioplux_config):

    bioplux = Bioplux(update_device=True,
                      update_channels=True,  # sets correct channels according to file
                      update_sampling_rate=True,  # sets sampling rates
                      **bioplux_config
                      )

    bioplux.data = bioplux.load_data(bioplux_datafile)

    lsl_transmitter = LSLTransmitter(device=bioplux,
                                     stream=STREAM_NAME_BIOPLUX,
                                     stream_type='name',
                                     transmit_data_in_chunks=False,
                                     augment_sampling_rate=True,
                                     )

    lsl_transmitter.start()

    print(f'streaming virtual data from file {bioplux_datafile} '
          f'to LSL on stream {lsl_transmitter.stream}'
          f'at a sampling rate of {lsl_transmitter.device["nominal_srate"]}.')

    print()
    print('device info:')
    for k, v in lsl_transmitter.device.items():
        print(f'- {k}: {v}')

    print()
    print('channel info:')
    for c in lsl_transmitter.channels:
        print(f'- {c}')

    duration_in_seconds = len(bioplux.data)/lsl_transmitter.device["nominal_srate"]
    show_each = 10
    for i in range(len(bioplux.data)):
        lsl_transmitter.push_data(bioplux.data[i])

        sent_percentage = i/(len(bioplux.data)-1)
        remaining_time = duration_in_seconds*(1.-sent_percentage)

        if not (i % show_each) or sent_percentage == 1.:
            print('\rSent {:.2f}%, {:.2f} secs remaining ...      '.format(
                sent_percentage*100, remaining_time),
                  end='' if sent_percentage != 1. else None)

    print('Done transmitting data.')
    lsl_transmitter.stop()


def bioplux_with_secured(bioplux_datafile=TEST_FILE_BIOPLUX, **bioplux_config):

    bioplux = Bioplux(update_device=True,
                      update_channels=True,  # sets correct channels according to file
                      update_sampling_rate=True,  # sets sampling rates
                      **bioplux_config
                      )

    bioplux.data = bioplux.load_data(bioplux_datafile)

    with LSLTransmitter(device=bioplux,
                        stream=STREAM_NAME_BIOPLUX,
                        stream_type='name',
                        transmit_data_in_chunks=False,
                        augment_sampling_rate=True,
                        ) as lsl_transmitter:

        print(f'streaming virtual data from file {bioplux_datafile} '
              f'to LSL on stream {lsl_transmitter.stream}'
              f'at a sampling rate of {lsl_transmitter.device["nominal_srate"]}.')

        print()
        print('device info:')
        for k, v in lsl_transmitter.device.items():
            print(f'- {k}: {v}')

        print()
        print('channel info:')
        for c in lsl_transmitter.channels:
            print(f'- {c}')

        duration_in_seconds = len(bioplux.data)/lsl_transmitter.device["nominal_srate"]
        show_each = 10
        for i in range(len(bioplux.data)):
            lsl_transmitter.push_data(bioplux.data[i])

            sent_percentage = i/(len(bioplux.data)-1)
            remaining_time = duration_in_seconds*(1.-sent_percentage)

            if not (i % show_each) or sent_percentage == 1.:
                print('\rSent {:.2f}%, {:.2f} secs remaining ...      '.format(
                    sent_percentage*100, remaining_time),
                      end='' if sent_percentage != 1. else None)

        print('Done transmitting data.')


def send_sample(sample: (str, Sample) = TEST_FILE_SAMPLE):

    sample = Sample.load(sample)
    sample.load_data()

    transmitter = []
    try:
        for i, device in enumerate(sample.setup.devices):
            t = LSLTransmitter(device=device,
                               stream=f'{device.name}',
                               stream_type='name',
                               augment_sampling_rate=True,
                               )

            print('---')
            print(f'streaming virtual data from file {sample.filename[i]} '
                  f'to LSL on stream {t.stream}'
                  f'at a sampling rate of {t.device["nominal_srate"]}.')

            print()
            print('device info:')
            for k, v in t.device.items():
                print(f'- {k}: {v}')

            print()
            print('channel info:')
            for c in t.channels:
                print(f'- {c}')

            transmitter.append(t)

        for t in transmitter:
            t.start()

        n_data = [len(d.data) for d in sample.setup.devices]

        durations_in_seconds = [
            n / t.device["nominal_srate"]
            for t, n in zip(transmitter, n_data)
        ]

        show_each = 10
        for i in range(max(n_data)):
            for t, d in zip(transmitter, sample.setup.devices):
                if i < len(d.data):
                    t.push_data(d.data[i])

            sent_percentage = i / (max(n_data) - 1)
            remaining_time = max(durations_in_seconds) * (1. - sent_percentage)

            if not (i % show_each) or sent_percentage == 1.:
                print('\rSent {:.2f}%, {:.2f} secs remaining ...      '.format(
                    sent_percentage * 100, remaining_time),
                    end='' if sent_percentage != 1. else None)

    finally:
        for t in transmitter:
            t.stop()

    print('Done transmitting data.')


if __name__ == '__main__':
    import argh
    argh.dispatch_commands([bioplux_run_start_stop, bioplux_with_secured, send_sample])

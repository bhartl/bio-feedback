""" Transmitting device or sample data to the Lab-Streaming-Layer using the bio-feedback framework

The applications (functions)

- `send_bioplux`
- `send_sample`

can be executed as main programs from the <PROJECT_ROOT> folder via

> python examples/pipeline/biofb_lsl_acquisition.py send_bioplux
> python examples/pipeline/biofb_lsl_acquisition.py send-sample

Using the -h argument shows the doc-string (help) for each application.

Above examples use per default predefined test-files to demonstrate how data is sent to the LSL.

The data can be acquired using different applications in the `examples/pipeline/*lsl_acquisition*` modules

Other data-files can be used and transmitted to the LSL.
"""

from biofb.pipeline import LSLTransmitter
from biofb.hardware.devices import Bioplux
from biofb.session import Sample

STREAM_NAME_BIOPLUX = 'VirtualPlux'

# Bioplux data
TEST_FILE_BIOPLUX = 'test/data/session/sample/bioplux/opensignals_0007800f315c_2021-01-19_15-03-08_converted.txt'

# Sample configuration in yml format (containing Bioplux and Unicorn data)
TEST_FILE_SAMPLE = 'test/data/session/sample/bioplux_and_unicorn_sample.yml'


def send_bioplux(datafile=TEST_FILE_BIOPLUX, mode='with_secured', **config):
    if mode == 'with_secured':
        return bioplux_with_secured(datafile=datafile, **config)
    elif mode == 'run_start_stop':
        return bioplux_run_start_stop(datafile=datafile, **config)
    else:
        raise NotImplementedError(mode)


def bioplux_run_start_stop(datafile=TEST_FILE_BIOPLUX, **config):

    bioplux = Bioplux(update_device=True,
                      update_channels=True,  # sets correct channels according to file
                      update_sampling_rate=True,  # sets sampling rates
                      **config
                      )

    bioplux.data = bioplux.load_data(datafile)

    lsl_transmitter = LSLTransmitter(device=bioplux,
                                     stream=STREAM_NAME_BIOPLUX,
                                     stream_type='name',
                                     transmit_data_in_chunks=False,
                                     terminate_when_empty=True,
                                     augment_sampling_rate=True,
                                     )

    lsl_transmitter.start()

    print(f'streaming virtual data from file {datafile} '
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

    lsl_transmitter.push_data(bioplux.data)
    lsl_transmitter.join()
    lsl_transmitter.stop()
    print('Done.')


def bioplux_with_secured(datafile=TEST_FILE_BIOPLUX, **config):

    bioplux = Bioplux(update_device=True,
                      update_channels=True,  # sets correct channels according to file
                      update_sampling_rate=True,  # sets sampling rates
                      **config
                      )

    bioplux.data = bioplux.load_data(datafile)

    with LSLTransmitter(device=bioplux,
                        stream=STREAM_NAME_BIOPLUX,
                        stream_type='name',
                        transmit_data_in_chunks=False,
                        terminate_when_empty=True,
                        augment_sampling_rate=True,
                        ) as lsl_transmitter:

        print(f'streaming virtual data from file {datafile} '
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

        lsl_transmitter.push_data(bioplux.data)
        lsl_transmitter.join()

    print('Done.')


def send_sample(sample_loadable: (str, Sample) = TEST_FILE_SAMPLE, offset=True):

    sample = Sample.load(sample_loadable)
    sample.load_data()

    transmitter = []
    try:
        for i, device in enumerate(sample.setup.devices):
            t = LSLTransmitter(device=device,
                               stream=f'{device.__class__.__name__}',
                               stream_type='name',
                               augment_sampling_rate=True,
                               terminate_when_empty=True,
                               verbose=(i == 0),
                               )

            print('---')
            print(f'streaming virtual data from file `{sample.filename[i]}` '
                  f'to LSL on stream `{t.stream}`'
                  f'at a sampling rate of `{t.device["nominal_srate"]}`.')

            print()
            print(f'device {device} info:')
            for k, v in t.device.items():
                print(f'- {k}: {v}')

            print()
            print('channel info:')
            for c, dc in zip(t.channels, device.channels):
                print(f'- device channel {dc} -> stream channel {c}')

            transmitter.append(t)

        # print verbosity information (we only allow one stream to be verbose)
        verbose_transmitter = [t for t in transmitter if t.verbose]
        verbose_slice = 0 if len(verbose_transmitter) == 1 else slice()
        print(f'\nTransmitter{"s" * (len(verbose_transmitter) > 1)}',
              f'{[str(t) for t in verbose_transmitter][verbose_slice]}',
              f'print{"s" * (len(verbose_transmitter) == 1)} status messages')

        # offset of different channel
        if offset:
            if isinstance(offset, bool):
                # cut off initial mismatch to shortest data-sample

                # get time of samples (ndata/sampling_rate)
                n_data = [len(d.data)/d.sampling_rate
                          for d in sample.setup.devices]

                # remove "overtime" of other samples"
                offset = [(nd - min(n_data))*d.sampling_rate
                          for d, nd in zip(sample.setup.devices, n_data)]

                # adjust as good as possible given the different smaping rates
                offset = [int(o + (d.sampling_rate - o % d.sampling_rate)) if o != 0 else 0
                          for o, d in zip(offset, sample.setup.devices)]

            print(f'\nUsing data-offset {offset} for the respective devices (resulting in a total of',
                  f'{[(len(d.data) - o)/d.sampling_rate for o, d in zip(offset, sample.setup.devices)]} secs',
                  f'of time-series data)\n')

        else:
            offset = [0]*sample.setup.n_devices

        assert len(offset) == sample.setup.n_devices

        # push device data to the queue, could also be done in chunks
        for t, d, o in zip(transmitter, sample.setup.devices, offset):
            t.push_data(d.data[o:])

        # start transmitter to transmit data received from the queue in a pus_data event
        for t in transmitter:
            t.start()

        for t in transmitter:
            t.join()

    finally:
        for t in transmitter:
            t.stop()

    print('Done with data-transmission')


if __name__ == '__main__':
    import argh
    argh.dispatch_commands([send_bioplux,
                            send_sample,
                            ])

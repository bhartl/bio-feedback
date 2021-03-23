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
    """ Send Bioplux data within `datafile` to the Lab Streaming Layer

    :param datafile: File-path containing Bioplux data
    :param mode: Either `with_secured` or `run_start_stop`, triggering the call of
                 either `bioplux_with_secured` or `bioplux_run_start_stop`, see respective docstrings.
    :param config: (Optional) Bioplux Device construction keyword-arguments
    """

    if mode == 'with_secured':
        return bioplux_with_secured(datafile=datafile, **config)
    elif mode == 'run_start_stop':
        return bioplux_run_start_stop(datafile=datafile, **config)
    else:
        raise NotImplementedError(mode)


def bioplux_run_start_stop(datafile=TEST_FILE_BIOPLUX, **config):
    """ Send Bioplux data within `datafile` in a background process to the Lab Streaming Layer
    using the manual start() and stop() mechanism of the `biofb.pipeline.LSLTransmitter`.

    :param datafile: File-path containing Bioplux data
    :param config: (Optional) Bioplux Device construction keyword-arguments
    """

    # instantiate Bioplux device
    bioplux = Bioplux(update_device=True,
                      update_channels=True,  # sets correct channels according to file
                      update_sampling_rate=True,  # sets sampling rates
                      **config
                      )

    # load Bioplux data
    bioplux.data = bioplux.load_data(datafile)

    # create LSLTransmitter instance
    lsl_transmitter = LSLTransmitter(device=bioplux,
                                     stream=STREAM_NAME_BIOPLUX,
                                     stream_type='name',
                                     transmit_data_in_chunks=False,
                                     terminate_when_empty=True,
                                     augment_sampling_rate=True,
                                     )

    # manually start background process for streaming
    lsl_transmitter.start()

    # print stream info
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

    # push data to the stream which are sent to the LSL in the lsl_transmitter._pusher
    # background process, communication via lsl_transmitter._queue
    lsl_transmitter.push_data(bioplux.data)

    # do something else ...

    # wait for data-transmission to finish
    lsl_transmitter.join()

    # manually stop background processes
    lsl_transmitter.stop()

    print('Done.')


def bioplux_with_secured(datafile=TEST_FILE_BIOPLUX, **config):
    """ Send Bioplux data within `datafile` in a background process to the Lab Streaming Layer
    using the `biofb.pipeline.LSLTransmitter` in a `with` block that takes care of the start()
    and stop() mechanism.

    :param datafile: File-path containing Bioplux data
    :param config: (Optional) Bioplux Device construction keyword-arguments
    """

    # instantiate Bioplux device
    bioplux = Bioplux(update_device=True,
                      update_channels=True,  # sets correct channels according to file
                      update_sampling_rate=True,  # sets sampling rates
                      **config
                      )

    # load Bioplux data
    bioplux.data = bioplux.load_data(datafile)

    # start streaming in a background process, stream is stopped when `with` block is done
    with LSLTransmitter(device=bioplux,
                        stream=STREAM_NAME_BIOPLUX,
                        stream_type='name',
                        transmit_data_in_chunks=False,
                        terminate_when_empty=True,
                        augment_sampling_rate=True,
                        ) as lsl_transmitter:

        # print stream info
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

        # push data to the stream which are sent to the LSL in the lsl_transmitter._pusher
        # background process, communication via lsl_transmitter._queue
        lsl_transmitter.push_data(bioplux.data)

        # do something else ...

        # wait for data-transmission to finish
        lsl_transmitter.join()

    print('Done.')


def send_sample(sample_loadable: (str, Sample) = TEST_FILE_SAMPLE, offset=True):
    f"""
    :param sample_loadable: Sample object or (path-to) dict-like object which can be loaded as Sample object, 
    defaults to {TEST_FILE_SAMPLE}
    :param offset: (i) Boolean controlling whether the data-arrays defined in the Sample are streamlined,  
                   i.e., if the number of sample-points (considering the sampling rate) are aligned such that
                   the transmission time for each data-array is as equal as possible;
                   or (ii) integer list, defining the offset for each data-array.
    """

    # Initialize Sample
    sample = Sample.load(sample_loadable)
    sample.load_data()

    # Generate LSLTransmitter for every device in the Sample
    transmitter = []
    try:
        for i, device in enumerate(sample.setup.devices):
            # Device specific transmitter
            t = LSLTransmitter(device=device,
                               stream=f'{device.__class__.__name__}',
                               stream_type='name',
                               augment_sampling_rate=True,
                               terminate_when_empty=True,
                               verbose=(i == 0),  # only show status messages for one transmitter for simplicity
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
        verbose_slice = 0 if len(verbose_transmitter) == 1 else slice(None, None, None)
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

                # adjust as good as possible given the different sampling rates
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

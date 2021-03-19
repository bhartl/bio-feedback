from biofb.hardware import Channel
import biofb.hardware.channels as chs
from biofb.hardware import Device
from numpy import loadtxt
from warnings import warn
from collections import defaultdict


class Bioplux(Device):
    """Helper class to interface Bioplux OpenSignals data.

    References:

    - [1] The different biosignalsplux sensors are listed on their
          `website <https://biosignalsplux.com/products/sensors.html>`_
    - [2] The OpenSignals r(evolution) can be downloaded
          `here <https://plux.info/software/43-opensignals-revolution-000000000.html>`_
          and can be used to open captured data-files (in the data/session/sample/bioplux/ folder).
    """

    NAME = 'Bioplux'

    SENSOR_TO_LABEL = dict((
        ("BVP", "BVP"),
        ("nSeq", "CNT"),
        ("ECG", "ECG"),
        ("EDA", "EDA"),
        ("EEG", "EEG"),
        ("EMG", "EMG"),
        ("EOG", "EOG"),
        ("TEMP", "TEMP"),
        ("RESPIRATION", "PZT"),
        ("DI", "DI"),
        ("CUSTOM", "FSW"),
    ))

    LABEL_TO_UNIT = defaultdict(
        lambda *args, **kwargs: '',
        (('EOG', 'mV'),
         ('ECG', 'mV'),
         ('PZT', 'V'),
         ('EEG', 'muV'),
         ('EDA', 'muS'),
         ('EMG', 'mV'),
         ('BVP', ''),
         ('CUSTOM', 'V'),
         ('DI', ''),
        )
    )

    # channel definitions    
    DI = chs.DI(name='DI', label="DI", sampling_rate=500, description="Digital input output.")
    EOG = chs.EOG(name='EOG', label="CH1", sampling_rate=500, description="Horizontal configuration (black right, red left, ref left).")
    ECG = chs.ECG(name='ECG', label="CH2", sampling_rate=500, description="Lean 1 configuration (ref top, red in, black out).")
    RESP = chs.PZT(name='RESPIRATION', label="CH3", sampling_rate=500, description="Placement between ECG electrodes.")
    EEG = chs.EEG(name='EEG', label="CH4", sampling_rate=500, description="FP1 (red, above left eye), FP2 (black, above right eye), M1 (behind ear above EOG ref).")
    EDA = chs.EDA(name='EDA', label="CH5", sampling_rate=500, description="Fingers right arm (red index, bottom third limb, black middle, bottom third limb).")
    EMG = chs.EMG(name='EMG', label="CH6", sampling_rate=500, description="Neck right side.")
    BPV = chs.BVP(name='BPV', label="CH7", sampling_rate=500, description="Blood Pressure Volume (index finger right).")
    FSW = chs.FSW(name='FSW', label="CH8", sampling_rate=500, description="Footswitch, RAW input.")

    # default channel arrangement of the Unicorn Hybrid Black
    CHANNELS = (DI, EOG, ECG, RESP, EEG, EDA, EMG, FSW, BPV)
    
    def __init__(self, name=NAME, channels=None, **kwargs):
        """Constructs a biofb Bioplux instance.

        :param name: Name of the device (str, defaults to Bioplux.NAME)
        :param channels: Channels of Bioplux setup (tuple or list, defaults to Bioplux.CHANNELS)
        """

        if channels is None:
            channels = tuple(c.copy() for c in Bioplux.CHANNELS)

        Device.__init__(self, name=name, channels=channels, **kwargs)

    def __str__(self) -> str:
        return f"<Bioplux: {self.name}>"

    def load_data(self, filename, update_device=False, update_channels=True, update_sampling_rate=True, **read_csv_kwargs):
        """Load data from `OpenSignals r(evolution) Recorder` data file.

        Only channels which are specified in the `biofb Bioplux` instance are loaded.

        :param filename: Data file to read form.
        :param update_device: Boolean which controls whether device data (such as name) are updated based on the data file (defaults to False).
        :param update_channels: Boolean which controls whether device's channels are updated based on the data file (defaults to True).
        :param update_sampling_rate: Boolean which controls whether device's channel's sampling rates are updated based on the data file (defaults to True).
        :returns: Data as `numpy` array of dimension (n_data, n_channels).
        """

        for k, v in self._load_data_kwargs.items():
            if k in locals():
                locals()[k] = v

        with open(filename, 'r') as f:
            f.readline()  # header
            config = eval(f.readline()[1:].strip())

        data = loadtxt(filename, **read_csv_kwargs)

        if len(config.keys()) > 1:
            raise NotImplementedError("Mutli-device measurement with biosignalsplux equipment.")

        device_name = list(config.keys())[0]

        # available information in data file
        device_config = config[device_name]
        device_connection = device_config['device connection']
        device_sampling_rate = device_config['sampling rate']
        device_resolution = device_config['resolution']  # resolution per channel
        device_firmware_version = device_config['firmware version']
        device_comments = device_config['comments']
        device_keywords = device_config['keywords']
        device_mode = device_config['mode']
        device_sync_interval = device_config['sync interval']
        device_date = device_config['date']
        device_time = device_config['time']
        device_channels = device_config['channels']
        device_sensor = device_config['sensor']
        device_label = device_config['label']
        device_column = device_config['column']
        device_special = device_config['special']
        device_sleeve_color = device_config['sleeve color']
        device_digital_IO = device_config['digital IO']
        device_converted_values = device_config['convertedValues']

        if not device_converted_values:
            warn("biosignalplux values have not been converted to physically meaningful units.")

        if update_device:
            self.name = device_name
            self.data = data

        if update_channels:
            channels = []
            for sensor, label in zip(device_sensor, device_label):
                name = sensor
                channel_label = self.sensor_to_label(name)

                sampling_rate = device_sampling_rate
                c = Channel.load(dict(name=sensor, label=channel_label, sampling_rate=sampling_rate))
                c.label = label

                channels.append(c)

            self.channels = [
                chs.DI(name=device_column[1], label='DI', sampling_rate=device_sampling_rate)
            ] + channels

        if update_sampling_rate:
            for c in self.channels:
                c.sampling_rate = device_sampling_rate

        data_columns = []
        for channel in self.channels:  # iterate current device channels

            found_channel = False
            for i, c in enumerate(device_column):  # and check, if device_column is present
                if i == 0:  # nSeq, not needed
                    continue

                if c == channel.label:
                    data_columns.append(i)
                    found_channel = True

                    if update_channels:
                        channel.label = self.sensor_to_label(channel.name)
                        channel.unit = self.LABEL_TO_UNIT[channel.label]  # if config else ''

                    break

            assert found_channel, f"Couldn't find device channel {channel.label} " \
                                  f"for sensor {channel.name} " \
                                  f"in loaded channels {[c.label for c in self.channels]}."

        assert len(data_columns) > 0, f"No data columns found for current device channels " \
                                      f"[{[c.name for c in self.channels]}]."

        return data[:, data_columns]

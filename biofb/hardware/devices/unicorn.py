import biofb.hardware.channels as chl
from biofb.hardware import Device
from pandas import read_csv
from numpy import array
from os.path import abspath


class Unicorn(Device):
    """Helper class to interface g.tec Unicorn data.

    References:

    - [1] The official `website for the g.tec unicorn 8-channel EEG device <https://www.unicorn-bi.com/>`_
          (the python interface for this hardware requires a licence key).
    """

    NAME = 'Unicorn'
    
    # channel definitions    
    EEG1 = chl.EEG(name='EEG 1', sampling_rate=250, description="Unicorn EEG 1 channel (Fz).")
    EEG2 = chl.EEG(name='EEG 2', sampling_rate=250, description="Unicorn EEG 2 channel (C3).")
    EEG3 = chl.EEG(name='EEG 3', sampling_rate=250, description="Unicorn EEG 3 channel (Cz).")
    EEG4 = chl.EEG(name='EEG 4', sampling_rate=250, description="Unicorn EEG 4 channel (C4).")
    EEG5 = chl.EEG(name='EEG 5', sampling_rate=250, description="Unicorn EEG 5 channel (Pz).")
    EEG6 = chl.EEG(name='EEG 6', sampling_rate=250, description="Unicorn EEG 6 channel (PO7).")
    EEG7 = chl.EEG(name='EEG 7', sampling_rate=250, description="Unicorn EEG 7 channel (Oz).")
    EEG8 = chl.EEG(name='EEG 8', sampling_rate=250, description="Unicorn EEG 8 channel (PO8).")
    ACCX = chl.ACC(name='Accelerometer X', axis=0, label='ACC X', sampling_rate=250, description="Unicorn EEG 8 channel (PO8).")
    ACCY = chl.ACC(name='Accelerometer Y', axis=1, label='ACC Y', sampling_rate=250, description="Unicorn EEG 8 channel (PO8).")
    ACCZ = chl.ACC(name='Accelerometer Z', axis=2, label='ACC Z', sampling_rate=250, description="Unicorn EEG 8 channel (PO8).")
    GYRX = chl.GYR(name='Gyroscope X', axis=0, label='GYR X', sampling_rate=250, description="Unicorn EEG 8 channel (PO8).")
    GYRY = chl.GYR(name='Gyroscope Y', axis=1, label='GYR Y', sampling_rate=250, description="Unicorn EEG 8 channel (PO8).")
    GYRZ = chl.GYR(name='Gyroscope Z', axis=2, label='GYR Z', sampling_rate=250, description="Gyroscope.")
    AKKU = chl.BAT(name='Battery Level', label='BATT', sampling_rate=250, description="Battery Level.")
    COUNT = chl.CNT(name='Counter', label='CNT', sampling_rate=250, description="Counter.")
    VALID = chl.QC(name='Validation Indicator', label='VALID', sampling_rate=250, description="Validation Indicator.")

    # default channel arrangement of the Unicorn Hybrid Black
    CHANNELS = (EEG1, EEG2, EEG3, EEG4, EEG5, EEG6, EEG7, EEG8,
                ACCX, ACCY, ACCZ, GYRX, GYRY, GYRZ,
                AKKU, COUNT, VALID)
    
    def __init__(self, name=NAME, channels=None, **kwargs):
        """Constructs a biofb Unicorn instance.

        :param name: Name of the device (str, defaults to Unicorn.NAME)
        :param channels: Channels of Unicorn Hybrid Black to work with (tuple or list, defaults to Unicorn.CHANNELS)
        """

        if channels is None:
            channels = tuple(c.copy() for c in Unicorn.CHANNELS)

        Device.__init__(self, name=name, channels=channels, **kwargs)

    def __str__(self) -> str:
        return f"<Unicorn: {self.name}>"

    def load_data(self, filename, update_device=False, **read_csv_kwargs):
        """Load data from `Unicorn Suit Hybrid Black Recorder` csv file.

        Only channels which are specified in the `biofb Unicorn` instance are loaded.

        :param filename: Csv data file to read form.
        :param update_device:  Boolean which controls whether device data are updated based on the data file (defaults to False).
        :returns: Data as `numpy` array of dimension (n_data, n_channels).
        """
        data = read_csv(abspath(filename), **{**self._load_data_kwargs, **read_csv_kwargs})

        if update_device:
            self._data = data

        loaded_channels = data.keys()

        for device_channel in self.channel_names:

            found_channel = False
            for loaded_channel in loaded_channels:
                if device_channel == loaded_channel:
                    found_channel = True
                    break

            assert found_channel, f"Couldn't find device channel {device_channel} in loaded channels {loaded_channels}."

        return array([data[channel].values for channel in self.channel_names]).T

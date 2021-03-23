from biofb.hardware import Device
from biofb.hardware.channels import EEG
from biofb.hardware.channels import QC


class Melomind(Device):
    """ Helper class to interface Melomind data

    **Note**: The Melomind data were captured using the open source DemoSKD.Android [2] from Melomind.
              The app was modified (by BH) to store the captured data (EEG 1, EEG 2, Quality 1, Quality 2)
              in a file in the Downloads-folder of an Android device.
              Improvements to this approach are welcome, also to gain access to life-data from the Melomind device.

    References:

    - [1] Official `website for the melomind device <https://www.melomind.com/en/home/>`_
    - [2] Github repo for the `DemoSKD.Android <https://github.com/mbt-administrator/DemoSDK.Android>`_ from Melomind.
    """

    NAME = 'Melomind'

    EEG1 = EEG(name='EEG 1', sampling_rate=250, description="Melomind EEG 1 channel.")
    EEG2 = EEG(name='EEG 2', sampling_rate=250, description="Melomind EEG 2 channel.")
    Q1 = QC(name='Q1', sampling_rate=250, description="Quality assessment of the EEG 1 channel (true sampling rate is 1 but we chose 250 to match the EEG channel).")
    Q2 = QC(name='Q2', sampling_rate=250, description="Quality assessment of the EEG 2 channel (true sampling rate is 1 but we chose 250 to match the EEG channel).")

    CHANNELS = (EEG1, EEG2, Q1, Q2)

    SENSOR_TO_LABEL = dict((
        (c.label, c)
        for c in CHANNELS
    ))

    def __init__(self, name=NAME, channels=None, **kwargs):
        """Constructs a biofb Bioplux instance.

        :param name: Name of the device (str, defaults to Bioplux.NAME)
        :param channels: Channels of Melomind setup (tuple or list, defaults to Melomind.CHANNELS)
        """

        if channels is None:
            channels = tuple(c.copy() for c in Melomind.CHANNELS)

        Device.__init__(self, name=name, channels=channels, **kwargs)

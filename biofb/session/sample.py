from biofb.io import Loadable
from biofb.session import Subject
from biofb.session import Setting
from biofb.hardware import Setup
from numpy import ndarray, asarray, arange
from datetime import datetime
from datetime import date
from datetime import time


class Sample(Loadable):
    """ The biofb sample-data analysis and acquisition class """

    time_format = "%H:%M"

    def __init__(self,
                 setup: (Setup, dict),
                 subject: (Subject, dict),
                 filename: str = "sample.dat",
                 setting: (Setting, dict, None) = None,
                 timestamp: (int, float, None) = None,
                 comments: (tuple, list) = (),
                 ):
        """Constructs a measurement `sample` instance.

        :param setup: The biofb hardware `Setup` used in the `Sample` (`Setup` or `dict`)
        :param subject: The `Subject` whose data is captured during the `Sample` (`Subject` or `dict`)
        :param filename: The file name on the system where the `Sample`-data are located or stored to (`str`, defaults to "sample.dat")
        :param timestamp: The timestamp of the `Sample`
                          (`int`, `float` or `None`, defaults to `None` -> current time stamp is used)
        :param comments: List of comments specific to the Sample (`tuple` or `list`, defaults to `()`)
        """

        Loadable.__init__(self)

        self._setup = None
        self.setup = setup

        self._subject = None
        self.subject = subject

        self._setting = None
        self.setting = setting

        self._filename = None
        self.filename = filename

        self._timestamp = None
        self.timestamp = timestamp

        self._comments = None
        self.comments = comments

        self._data = None

    @property
    def filename(self) -> str:
        return self._filename

    @filename.setter
    def filename(self, value: str):
        self._filename = value

    @property
    def timestamp(self) -> float:
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value: (int, float, None)):
        if value is None:
            value = datetime.now().timestamp()
        elif isinstance(value, str):
            converted = None
            formats = [
                "%Y-%m-%d_%H-%M-%S",
                "%Y-%m-%d %H-%M-%S",
                "%Y-%m-%d_%H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
                "%Y%m%d_%H-%M-%S",
                "%Y%m%d %H-%M-%S",
                "%Y%m%d_%H:%M:%S",
                "%Y%m%d %H:%M:%S",
                "%Y%m%d_%H%M%S",
                "%Y%m%d%H%M%S",
                "%Y%m%d%H%M%S",
            ]

            for format in formats:
                try:
                    converted = datetime.strptime(value, format).timetuple()
                except ValueError:
                    pass

            if converted is None:
                raise ValueError(f"Date format not recognized: {value}")

            value = datetime(*converted[:6]).timestamp()

        self._timestamp = value

    @property
    def acquisition_datetime(self) -> datetime:
        return datetime.fromtimestamp(self.timestamp)

    @property
    def acquisition_date(self) -> date:
        return date.fromtimestamp(self.timestamp)

    @property
    def capture_time(self) -> time:
        return datetime.fromtimestamp(self.timestamp).time()

    @property
    def subject(self) -> Subject:
        return self._subject

    @subject.setter
    def subject(self, value: (dict, Subject)):
        self._subject = Subject.load(value)

    @property
    def setting(self) -> Setting:
        return self._setting

    @setting.setter
    def setting(self, value: (dict, Setting)):
        self._setting = Setting.load(value)

    @property
    def setup(self) -> Setup:
        return self._setup

    @setup.setter
    def setup(self, value: (dict, Setup)):
        self._setup = Setup.load(value)
        self._setup._sample = self

    def comment(self, value: str):
        self.comments.append(value)

    @property
    def comments(self) -> list:
        return self._comments

    @comments.setter
    def comments(self, value: (tuple, list, set)):
        self._comments = list(value) if not isinstance(value, str) else [value]

    @property
    def meta_data(self) -> dict:
        return dict(
            subject=self.subject,
            setting=self.setting,
            timestamp=self.timestamp,
        )

    @property
    def data(self) -> list:
        if self._data is None:
            self._data = [None] * self.setup.n_devices

        return self._data

    @data.setter
    def data(self, value: list):
        self._data = value

    @property
    def time(self) -> ndarray:
        time_data = []

        devices = self.setup.devices
        data = self.data

        for device, device_data in zip(devices, data):
            i = 0
            device_data = asarray(device_data)
            device_time = []

            for channels in device.channels:
                device_time.append(arange(0, len(device_data[:, i])) / channels.sampling_rate)
                i += 1

            time_data.append(asarray(device_time).T)

        return time_data

    @property
    def labels(self) -> list:

        labels = []

        for device in self.setup.devices:
            for channel in device.channels:
                labels.append(channel.name)

        return labels

    def load_data(self):
        try:
            filenames = self.filename if not isinstance(self.filename, str) else [self.filename]
            devices = self.setup.devices

            device_data = []
            for device, filename in zip(devices, filenames):
                data = device.load_data(filename)
                device_data.append(data)

            self._data = device_data

        except (OSError, FileNotFoundError) as ex:
            raise FileNotFoundError(f'Could not load `{self.filename}` via device: `{ex}`.')

    def __str__(self):
        return f"<Sample: Subject {self.subject.identity} at {self.acquisition_datetime}>"

    @property
    def state(self) -> list:

        # receive data from all devices
        chunk_data = self.setup.receive_data()

        # here data-preprocessing might be done
        # ...

        # return only values, not time-stamps
        return [value for time, value in chunk_data]

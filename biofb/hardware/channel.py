from biofb.io import Loadable
from biofb.signal import filter
from numpy import asarray, arange, linspace, ndarray
from copy import deepcopy


class Channel(Loadable):
    """Channel used in a bio-controller hardware device."""

    def __init__(self, name: str, sampling_rate: int, label: (str, None) = None, unit: (None, str) = "",
                 description: str = ""):
        """Constructs a bio-controller hardware device `Channel` instance.

        :param name: `name` of the `Channel` (str).
        :param sampling_rate: Sampling rate of the `Channel` in Hz (int).
        :param unit: sampling unit of the channel (str, defaults to "").
        :param description: description of the device (str, defaults to "").
        """

        Loadable.__init__(self)

        self._name = None
        self.name = name

        self._label = None
        self.label = label

        self._sampling_rate = None
        self.sampling_rate = sampling_rate

        self._description = None
        self.description = description

        self._device = None
        self._data = None

        self._unit = None
        self.unit = unit

    def to_dict(self):
        return dict(name=self.name,
                    sampling_rate=self.sampling_rate,
                    label=self.label,
                    description=self.description,
                    )

    def copy(self):
        channel = self.load(self.to_dict())
        if self._device is not None:
            channel._device = self._device

        return channel

    @classmethod
    def load(cls, value):
        """ Loads channel instance based on the `value_dict` argument (`Channel` or `dict`).

        If `name` attribute refers to a specific channel within the `biofb.hardware.channels` package,
        the respective special channel is loaded.

        :param value: `Channel` or `dict` object
        :return:
        """

        from biofb.hardware import channels as channels_module

        if isinstance(value, dict):
            channel_cls = getattr(channels_module, value['name'], getattr(channels_module, value.get('label', 'None'), cls))

        elif isinstance(value, cls):
            channel_cls = value.__class__

            if channel_cls == cls:
                return value

            value = value.to_dict()

        else:
            raise NotImplementedError(f'Don`t understand type `{type(value)}` of value_dict `{value}`')

        return channel_cls(**value)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def label(self) -> str:
        return self._label if self._label is not None else self._name

    @label.setter
    def label(self, value: str):
        self._label = value

    @property
    def unit(self) -> str:
        return self._unit

    @unit.setter
    def unit(self, value: str):
        self._unit = value

    @property
    def type(self) -> str:
        return self.__class__.__name__

    @property
    def sampling_rate(self) -> int:
        return self._sampling_rate

    @sampling_rate.setter
    def sampling_rate(self, value: int):
        assert value > 0, f"Only positive sampling rates are allowed (provided `value_dict`: {value})."
        self._sampling_rate = value

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

    def __str__(self) -> str:

        class_name = self.__class__.__name__
        if class_name != 'Channel':
            class_name = class_name + '-Channel'

        return f"<{class_name}: {self.name}>"

    def apply_notch(self, update_data=True, **kwargs):
        """ Evaluates notch-filter `biofb.signal.preprocessing.apply_notch` to channel data.

        :param update_data: Boolean which controls wheter the channel data are updated after the notch filter.
        :param kwargs: Keyword arguments forwarded to `biofb.signal.preprocessing.apply_notch`
                       (see `apply_notch` documentation for details).
        :returns: Filtered data.
        """
        filtered = filter.apply_notch(self.data, sampling_rate=self.sampling_rate, **kwargs)

        if update_data:
            self.data = filtered
            return self.data

        return filtered

    def apply_bandpass(self, Wn: ndarray, N: int = 10, filtfilt=True, update_data=True, **kwargs):
        """ Evaluates bandpass-filter `biofb.signal.preprocessing.apply_sos_filter` to channel data.

        :param Wn: Frequency window defining the lower and higher bandpass frequencies (array_like).
                   For digital units, `Wn` is the same units as `sampling_rate`.
        :param N: The order of the filter (int, defaults to 10).
        :param update_data: Boolean which controls wheter the channel data are updated after the notch filter.
        :param filtfilt: Boolean specifying whether to use `scipy.signal.filtfilt` or `signal.lfilter` (defaults to False).
        :param kwargs: Keyword arguments forwarded to `biofb.signal.preprocessing.apply_sos_filter`
                       (keywords `sampling_rate`, `return_filter` and `sos_filter` are preset,
                        for the remaining keyword arguments see documentation of `apply_sos_filter`).
        :returns: Filtered data.
        """
        filtered = filter.apply_sos_filter(x=self.data,
                                           N=N,
                                           Wn=Wn,
                                           sos_filter='bandpass',
                                           sampling_rate=self.sampling_rate,
                                           return_filter=False,
                                           filtfilt=filtfilt,
                                           **kwargs)

        if update_data:
            self.data = filtered
            return self.data

        return filtered

    def apply_bandstop(self, Wn: ndarray, N: int = 10, filtfilt=True, update_data=True, **kwargs):
        """ Evaluates bandstop-filter `biofb.signal.preprocessing.apply_sos_filter` to channel data.

        :param Wn: Frequency window defining the lower and higher bandstop frequencies (array_like).
                   For digital units, `Wn` is the same units as `sampling_rate`.
        :param N: The order of the filter (int, defaults to 10).
        :param update_data: Boolean which controls wheter the channel data are updated after the notch filter.
        :param filtfilt: Boolean specifying whether to use `scipy.signal.filtfilt` or `signal.lfilter` (defaults to False).
        :param kwargs: Keyword arguments forwarded to `biofb.signal.preprocessing.apply_sos_filter`
                       (keywords `sampling_rate`, `return_filter` and `sos_filter` are preset,
                        for the remaining keyword arguments see documentation of `apply_sos_filter`).
        :returns: Filtered data.
        """
        filtered = filter.apply_sos_filter(x=self.data,
                                           N=N,
                                           Wn=Wn,
                                           sos_filter='bandstop',
                                           sampling_rate=self.sampling_rate,
                                           return_filter=False,
                                           filtfilt=filtfilt,
                                           **kwargs)

        if update_data:
            self.data = filtered
            return self.data

        return filtered

    def apply_lowpass(self, Wn: (int, float), N: int = 10, filtfilt=True, update_data=True, **kwargs):
        """ Evaluates lowpass-filter `biofb.signal.preprocessing.apply_notch` to channel data.

        :param Wn: Lower critical frequency of lowpass filter (int, float).
                   For digital units, `Wn` is the same units as `sampling_rate`.
        :param N: The order of the filter (int, defaults to 10).
        :param update_data: Boolean which controls wheter the channel data are updated after the notch filter.
        :param filtfilt: Boolean specifying whether to use `scipy.signal.filtfilt` or `signal.lfilter` (defaults to False).
        :param kwargs: Keyword arguments forwarded to `biofb.signal.preprocessing.apply_sos_filter`
                       (keywords `sampling_rate`, `return_filter` and `apply_sos_filter` are preset,
                        for the remaining keyword arguments see documentation of `apply_sos_filter`).
        :returns: Filtered data.
        """
        filtered = filter.apply_sos_filter(x=self.data,
                                           N=N,
                                           Wn=Wn,
                                           sos_filter='lowpass',
                                           sampling_rate=self.sampling_rate,
                                           return_filter=False,
                                           filtfilt=filtfilt,
                                           **kwargs)

        if update_data:
            self.data = filtered
            return self.data

        return filtered

    def apply_highpass(self, Wn: (int, float), N: int = 10, filtfilt=True, update_data=True, **kwargs):
        """ Evaluates highpass-filter `biofb.signal.preprocessing.apply_notch` to channel data.

        :param Wn: Lower critical frequency of lowpass filter (int, float).
                   For digital units, `Wn` is the same units as `sampling_rate`.
        :param N: The order of the filter (int, defaults to 10).
        :param update_data: Boolean which controls wheter the channel data are updated after the notch filter.
        :param filtfilt: Boolean specifying whether to use `scipy.signal.filtfilt` or `signal.lfilter` (defaults to False).
        :param kwargs: Keyword arguments forwarded to `biofb.signal.preprocessing.apply_sos_filter`
                       (keywords `sampling_rate`, `return_filter` and `apply_sos_filter` are preset,
                        for the remaining keyword arguments see documentation of `apply_sos_filter`).
        :returns: Filtered data.
        """
        filtered = filter.apply_sos_filter(x=self.data,
                                           N=N,
                                           Wn=Wn,
                                           sos_filter='highpass',
                                           sampling_rate=self.sampling_rate,
                                           return_filter=False,
                                           filtfilt=filtfilt,
                                           **kwargs)

        if update_data:
            self.data = filtered
            return self.data

        return filtered

    @property
    def data(self):
        if self._data is None:
            if self._device is not None:
                return [channel_data
                        for channel, channel_data in zip(self._device.channels, self._device.data.T)
                        if channel is self][0]

        return self._data

    @data.setter
    def data(self, value):
        if self._device is not None:
            for i, channel in enumerate(self._device.channels):
                if channel is self:
                    self._device.data[:, i] = value

        if self._data is not None:
            self._data[:] = value

    @property
    def time(self):
        data = self.data
        time = linspace(0, len(data)/self.sampling_rate, len(data), endpoint=False)

        return time

    def plot(self, data, ax=None, label_by='label', figure_kwargs=(), **plot_kwargs):
        """Plot provided channel data.

        :param data: Channel data array (multiple data for each channel are possible,
                     dimensions must be `[n_samples per channel, ...]`)
        :param ax: (Optional) matplotlib axis object for plotting.
        :param label_by: (Optional) Channel attribute name which is used as y-label in the ax plot.
        :param figure_kwargs: (Optional) keywords dict object for `matplotlib.pyplot.subplots`
                              subplot generator in case `ax` is not provided.
        :param plot_kwargs: (Optional) Keyword arguments for plot routine.
        :returns: `ax` object.
        """
        if ax is None:
            import matplotlib.pyplot as plt
            plt.figure(**figure_kwargs)
            ax = plt.gca()

        data = asarray(data)
        if data.ndim == 1:
            data = [data]

        plot_kwargs = deepcopy(plot_kwargs)
        for i in range(len(data)):
            t = arange(0, len(data[i])) / self.sampling_rate

            label = plot_kwargs.pop('label', None)
            sample_label = None if label is None else (label + (f' {i}' * (len(data) > 1)))

            ax.plot(t, data[i], label=sample_label, **plot_kwargs)

        y_label = getattr(self, label_by)  # get channel attribute to label y axis
        ax.set_ylabel(y_label)
        ax.set_xlabel('Time [s]')

        return ax

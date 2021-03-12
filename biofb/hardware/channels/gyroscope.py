from biofb.hardware import Channel


class GYR(Channel):
    """ Gyroscope (GYR) sensor channel

        **Note**: GYR-XYZ channels are used by the **g.tec Unicorn**
    """

    def __init__(self, axis: (int, str), *args, **kwargs):
        """

        :param args: Arguments forwarded to `Channel` constructor.
        :param kwargs: Keyword arguments forwarded to `Channel` constructor.
        """

        Channel.__init__(self, *args, **kwargs)

        self._axis = None
        self.axis = axis

    @property
    def axis(self) -> (int, str):
        return self._axis

    @axis.setter
    def axis(self, value: (int, str)):
        assert value in (0, 1, 2, 'X', 'Y', 'Z')
        self._axis = value

    def to_dict(self):
        return dict(name=self.name,
                    sampling_rate=self.sampling_rate,
                    label=self.label,
                    description=self.description,
                    axis=self.axis,
                    )

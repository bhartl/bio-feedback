from biofb.hardware import Channel


class TEMP(Channel):
    """ Temperature (TEMP) sensor channel

        **Note**: A PZT channel may be used by the **bioplux** hub
    """

    def __init__(self, *args, **kwargs):
        """

        :param args: Arguments forwarded to `Channel` constructor.
        :param kwargs: Keyword arguments forwarded to `Channel` constructor.
        """

        Channel.__init__(self, *args, **kwargs)

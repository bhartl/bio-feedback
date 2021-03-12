from biofb.hardware import Channel


class BAT(Channel):
    """ Battery (BAT) sensor channel

        **Note**: A BAT channel is used by the **g.tec Unicorn**
    """

    def __init__(self, *args, **kwargs):
        """

        :param args: Arguments forwarded to `Channel` constructor.
        :param kwargs: Keyword arguments forwarded to `Channel` constructor.
        """

        Channel.__init__(self, *args, **kwargs)

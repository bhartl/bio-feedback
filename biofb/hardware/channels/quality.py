from biofb.hardware import Channel


class QC(Channel):
    """ Quality Channel

        **Note**: QT channels are used by the **melomind** and **g.tec Unicorn** hardware
    """

    def __init__(self, *args, **kwargs):
        """

        :param args: Arguments forwarded to `Channel` constructor.
        :param kwargs: Keyword arguments forwarded to `Channel` constructor.
        """

        Channel.__init__(self, *args, **kwargs)

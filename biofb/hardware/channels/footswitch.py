from biofb.hardware import Channel


class FSW(Channel):
    """ Footswitch device to mark events during acquisition

        **Note**: AN FSW channel may be used by the **bioplux** hub

        - as analog usually on channel 8 CH8
        - or as digital input.
    """

    def __init__(self, *args, **kwargs):
        """

        :param args: Arguments forwarded to `Channel` constructor.
        :param kwargs: Keyword arguments forwarded to `Channel` constructor.
        """

        Channel.__init__(self, *args, **kwargs)

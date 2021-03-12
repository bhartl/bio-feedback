from biofb.hardware import Channel


class PZT(Channel):
    """ Respiration-Piezo (PZT) sensor channel:  a sensitive girth sensor worn using an
        easy fitting high durability woven elastic band.

        **Note**: A PZT channel may be used by the **bioplux** hub
    """

    def __init__(self, *args, **kwargs):
        """

        :param args: Arguments forwarded to `Channel` constructor.
        :param kwargs: Keyword arguments forwarded to `Channel` constructor.
        """

        Channel.__init__(self, *args, **kwargs)

from biofb.hardware import Channel


class EMG(Channel):
    """ **E**lectro**m**yo**g**raphy: Channel for electrodiagnostic medicine technique for evaluating and
        recording the electrical activity produced by skeletal muscles.

        **Note**: AN EMG channel may be used by the **bioplux** hub
    """

    def __init__(self, *args, **kwargs):
        """

        :param args: Arguments forwarded to `Channel` constructor.
        :param kwargs: Keyword arguments forwarded to `Channel` constructor.
        """

        Channel.__init__(self, *args, **kwargs)

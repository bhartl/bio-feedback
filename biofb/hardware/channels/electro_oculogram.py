from biofb.hardware import Channel


class EOG(Channel):
    """ **E**lectro**o**culo**g**raphy: Channel for electrodiagnostic medicine technique for measuring
        the corneo-retinal standing potential that exists between the front and the back of the human eye.

        **Note**: AN EOG channel may be used by the **bioplux** hub

    """

    def __init__(self, *args, **kwargs):
        """

        :param args: Arguments forwarded to `Channel` constructor.
        :param kwargs: Keyword arguments forwarded to `Channel` constructor.
        """

        Channel.__init__(self, *args, **kwargs)

from biofb.hardware import Channel


class EDA(Channel):
    """ Electrodermal activity (**EDA**; also known as galvanic skin response, or **GSR**)

        refers to the variation of the electrical conductance of the skin in response to sweat secretion
        (often in minute amounts) [1](https://imotions.com/blog/eda/).

        **Note**: AN EDA channel may be used by the **bioplux** hub
    """

    def __init__(self, *args, **kwargs):
        """

        :param args: Arguments forwarded to `Channel` constructor.
        :param kwargs: Keyword arguments forwarded to `Channel` constructor.
        """

        Channel.__init__(self, *args, **kwargs)

from biofb.io import Loadable


class Location(Loadable):
    """Location of a measurement."""

    def __init__(self, name="", comment=""):
        """Constructs a bio-controller session `Location` instance.

        :param name: `name` identifier of the `Location`.
        :param comment:
        """
        Loadable.__init__(self)

        self._name = None
        self.name = name

        self._comment = None
        self.comment = comment

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def comment(self) -> str:
        return self._comment

    @comment.setter
    def comment(self, value: str):
        self._comment = value

    def __str__(self):
        return f"<Location: {self.name}>"

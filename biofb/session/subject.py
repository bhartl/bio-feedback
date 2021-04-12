from biofb.io import Loadable
from pandas import read_csv
from os.path import isfile
from os.path import abspath


class Subject(Loadable):
    """Subject involved in a measurement."""

    def __init__(self, identity: (int, str), gender=None, age=None, comment="", id_file=None, respect_privacy=True):
        """Constructor of Subject

        :param identity: A `Subject`'s identifier (str).
        :param comment: Comment about the subject (str, defaults to "").
        :param gender: A `Subject`'s gender, stored lowercase (str or None, defaults to None)
        :param age: A `Subject`'s age (int or None, defaults to None)
        :param id_file: A csv-file for identity-name lookup (str or None, defaults to None)
        :param respect_privacy: Boolean controlling whether data-privacy is active:
                                name or initials can't be looked up if True (defaults to True).
        """

        Loadable.__init__(self)

        self._identity = None
        self.identity = identity

        self._gender = None
        self.gender = gender

        self._age = None
        self.age = age

        self._comment = None
        self.comment = comment
        
        self._id_file = None
        self.id_file = id_file

        self._respect_privacy = None
        self.respect_privacy = respect_privacy

    @property
    def identity(self) -> (int, str):
        return self._identity

    @identity.setter
    def identity(self, value: (int, str)):
        self._identity = value

    @property
    def gender(self) -> str:
        return self._gender

    @gender.setter
    def gender(self, value: str):
        if value is not None:
            value = str(value).lower()

        self._gender = value

    @property
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, value: int):
        self._age = value

    @property
    def id_file(self) -> str:
        return self._id_file

    @id_file.setter
    def id_file(self, value: str):
        self._id_file = value

    @property
    def comment(self) -> str:
        return self._comment

    @comment.setter
    def comment(self, value: str):
        self._comment = value

    @property
    def name(self) -> str:
        assert not self._respect_privacy, "Privacy is respected, name can not be looked up."
        assert self.id_file is not None, "No id-lookup-file specified."

        id_file = abspath(self.id_file)
        assert isfile(id_file), f"Subject identity-file {id_file} not found."

        df_ids = read_csv(id_file)
        subject_id = (df_ids['ID'] == self.identity).to_numpy()
        assert any(subject_id), f"Subject identity {self.identity} not found."

        name_df = df_ids[subject_id]
        return f"{name_df['Given Name'].values[0]} {name_df['Name'].values[0]}"

    @property
    def initials(self) -> str:
        return ''.join([s[0] for s in self.name.split(" ")])

    def __str__(self):
        try:
            return f"<Subject: {self.initials}>"
        except AssertionError:
            return f"<Subject: {self.identity}>"

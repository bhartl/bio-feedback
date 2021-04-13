import random

from biofb.io import Loadable
from os.path import isfile
from os.path import abspath
import pandas as pd
import os


class Subject(Loadable):
    """Subject involved in a measurement."""

    ID_RANGE = (100000, 999999)
    """Integer Range to choose random numbers for identities from (6 digit numbers)"""

    def __init__(self, identity: (int, str), gender: str = None, year_of_birth: int = None, comment: str = "",
                 id_file: (str, None) = "data/.private/subject-id.csv",
                 respect_privacy: bool = True,
                 name: (str, tuple, dict, None) = None):
        """Constructor of Subject

        :param identity: A `Subject`'s identifier (str).
        :param comment: Comment about the subject (str, defaults to "").
        :param gender: A `Subject`'s gender, stored lowercase (str or None, defaults to None)
        :param year_of_birth: A `Subject`'s age (int or None, defaults to "data/.private/subject-id.csv")
        :param id_file: A csv-file for identity-name lookup (str or None, defaults to None)
        :param respect_privacy: Boolean controlling whether data-privacy is active:
                                name or initials can't be looked up if True (defaults to True).
        :param name: Name of the subject which is handled with the privacy policy (defaults to None).
                     If a name is specified, it is forwarded to the name property (check name property doc for
                     possible options) and stored in the specified id-privacy file.
        """

        Loadable.__init__(self)

        self._identity = None
        self.identity = identity

        self._gender = None
        self.gender = gender

        self._year_of_birth = None
        self.year_of_birth = year_of_birth

        self._comment = None
        self.comment = comment
        
        self._id_file = None
        self.id_file = id_file

        self._respect_privacy = None
        self.respect_privacy = respect_privacy

        self.name = name

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
    def year_of_birth(self) -> int:
        return self._year_of_birth

    @year_of_birth.setter
    def year_of_birth(self, value: int):
        self._year_of_birth = value

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
    def respect_privacy(self) -> bool:
        return self._respect_privacy

    @respect_privacy.setter
    def respect_privacy(self, value: bool):
        self._respect_privacy = value

    @property
    def name(self) -> str:
        assert not self._respect_privacy, "Privacy is respected, name can not be looked up."
        assert self.id_file is not None, "No id-lookup-file specified."

        id_file = abspath(self.id_file)
        assert isfile(id_file), f"Subject identity-file {id_file} not found."

        df_ids = pd.read_csv(id_file)
        subject_id = (df_ids['ID'] == self.identity).to_numpy()
        assert any(subject_id), f"Subject identity {self.identity} not found."

        name_df = df_ids[subject_id]
        return f"{name_df['Given Name'].values[0]} {name_df['Name'].values[0]}"

    @name.setter
    def name(self, name: (str, tuple, dict)):
        """ Sets the name of a subject if a privacy-file is specified. A subject is identified via the
        identifier in the id_file. If a corresponding line is present in the id_file, the subject is
        updated. If a new identifier is specified, a new line will be added.

        name: name of subject, either a space-separated string,
              tuple of firstnames and lastname,
              dictionary specifying the "First Name" and the "Surname".
        """

        if name is None:
            return

        assert self.id_file is not None, "No id-lookup-file specified."

        # extract first name and surname from parameter
        given_name, surname = None, None
        if isinstance(name, str):
            name = [n for n in name.split(' ') if n != '']

        if isinstance(name, tuple) or isinstance(name, list):
            given_name = " ".join(name[:-1])
            surname = name[-1]

        if isinstance(name, dict):
            given_name = self.get_first_in(name, keys=['Given Name', 'First Name'], exchangeable=(' ', '_', '-'), upper=True, lower=True)
            surname = self.get_first_in(name, keys=['Surname', 'Family Name', 'Name'], exchangeable=(' ', '_', '-'), upper=True, lower=True)

        assert isinstance(given_name, str)
        assert isinstance(surname, str)

        # generate new entry
        id_df = pd.DataFrame([{'ID': self.identity, 'Given Name': given_name, 'Name': surname}])
        try:
            id_data = pd.read_csv(self.id_file)
            header = len(id_data) == 0

            if self.identity in id_data.ID.tolist():
                # id present in current id_file -> update entry
                id_data.loc[id_data.ID == self.identity, 'Name'] = surname
                id_data.loc[id_data.ID == self.identity, 'Given Name'] = given_name
                id_data.to_csv(self.id_file, index=False, header=True, mode='w')
            else:
                # new id, append line
                id_df.to_csv(self.id_file, index=False, header=header, mode='a')

        except FileNotFoundError:
            # new id file, create file
            os.makedirs(os.path.split(self.id_file)[0], exist_ok=True)
            id_df.to_csv(self.id_file, index=False, header=True, mode='w')

    @property
    def initials(self) -> str:
        return ''.join([s[0] for s in self.name.split(" ")])

    def __str__(self):
        try:
            return f"<Subject: {self.initials}>"
        except AssertionError:
            return f"<Subject: {self.identity}>"

    @classmethod
    def get_random_identifier(cls, id_file=None, id_range=ID_RANGE, n_max=int(1e6)):
        """ get random identifier in the `id_range` (if specified, not present in id_file)

        :param id_file: File (or None) containing identifier information (Optional).
        :param id_range: tuple of lower and upper integer for random identifier generation
                         (defaults to Subject.ID_RANGE).
        :param n_max: Maximum number of tries to generate new identifier.
        """

        identity = random.randint(*id_range)

        id_list = ()
        if id_file is not None:
            try:
                id_data = pd.read_csv(id_file)
                id_list = id_data.ID.tolist()
            except FileNotFoundError:
                pass

        i = 0
        while identity in id_list:
            if i >= n_max:
                raise KeyError(f"Could not generate unique random number in range {id_range} in {n_max} tries.")

            identity = random.randint(*id_range)
            i += 1

        return identity

    @classmethod
    def from_terminal(cls, avoid=('name', ), **defaults):

        subject = super().from_terminal(avoid=avoid, **defaults)
        assert isinstance(subject, Subject)

        id_list = ()
        first_name, given_name = None, None
        if subject.id_file is not None:
            given_name = input(f'Given Name: ')
            first_name = input(f'Name: ')

            try:
                id_data = pd.read_csv(subject.id_file)
                id_list = id_data.ID.tolist()

            except FileNotFoundError:
                id_list = ()

        identity, id_decision = subject.identity, True
        while identity in ("", None) or identity in id_list:
            if id_decision and identity in id_list:
                print(f'WARNING: ID {subject.identity} taken.')

            new_identity = None
            if id_decision:
                id_decision = input(f"identity (random): ")
                if id_decision.lower().strip() != "":
                    new_identity = id_decision
                    id_decision = True
                else:
                    id_decision = False

            if not id_decision:
                new_identity = subject.get_random_identifier(id_file=subject.id_file,
                                                             id_range=subject.ID_RANGE)

            identity = new_identity

        subject.identity = identity

        if first_name is not None and given_name is not None:
            subject.name = {'Given Name': given_name, 'Name': first_name}

        return subject

from __future__ import annotations
from biofb.io import Loadable
from os import path
import yaml


class SessionDatabase(Loadable):
    def __init__(self, samples: (list, tuple) = (), **kwargs):

        Loadable.__init__(self)

        self._samples = None
        self.samples = samples

        self.other_kwargs = kwargs

    @property
    def samples(self) -> list:
        return self._samples

    @samples.setter
    def samples(self, value: (list, tuple)):
        from biofb.session import Sample

        if value is None:
            return

        self._samples = [(m if isinstance(m, Sample) else Sample(**m)) for m in value]

    @property
    def meta(self) -> list:
        return [m.meta_data for m in self._samples]

    @property
    def data(self) -> list:
        return [m.data for m in self._samples]

    @property
    def time(self) -> list:
        return [m.time for m in self._samples]

    def get_data(self, indexer: (int, list, tuple, None) = None) -> list:
        data = []

        if indexer is not None:
            if not hasattr(indexer, '__iter__'):
                indexer = [indexer]

            data.extend([self._samples[i].data for i in range(indexer)])

        return data

    @staticmethod
    def load(filename: str, **kwargs) -> SessionDatabase:

        try:
            with open(filename, 'r') as s:

                db = yaml.load(s, Loader=yaml.Loader)

                if 'meta_data' in db and isinstance(db['meta_data'], str):

                    meta_data = db['meta_data']
                    if path.isfile(path.abspath(meta_data)):
                        meta_data = Loadable.load_dict_like(meta_data)

                        if 'ids' in meta_data:
                            ids = meta_data['ids']

                            for sample in db['samples']:
                                keys = sample.keys()

                                for k in keys:
                                    try:
                                        possible_meta_data_key = sample[k]
                                        sample[k] = ids[possible_meta_data_key]

                                    except (TypeError, KeyError):
                                        pass

                return SessionDatabase(**{**db, **kwargs})
        except FileNotFoundError as fnfe:
            if path.isabs(filename):
                raise fnfe

            return SessionDatabase.load(path.abspath(filename), **kwargs)

    def __add__(self, other: (SessionDatabase, tuple, list)) -> SessionDatabase:
        self_samples = [s for s in self.samples]

        if isinstance(other, SessionDatabase):
            other_samples = [o for o in other.samples]
        else:
            assert hasattr(other, '__iter__'), "Other must be iterable of samples or SessionDatabase instance."
            other_samples = [o for o in other]

        return SessionDatabase(samples=self_samples + other_samples, **self.other_kwargs)

    def __iadd__(self, other):

        if isinstance(other, SessionDatabase):
            other_samples = [o for o in other.samples]
        else:
            assert hasattr(other, '__iter__'), "Other must be iterable of samples or SessionDatabase instance."
            other_samples = [o for o in other]

        self.samples.extend(other_samples)

        return self

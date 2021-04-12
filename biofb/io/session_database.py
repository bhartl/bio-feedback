from __future__ import annotations
from biofb.io import Loadable
from os import path
import yaml
from collections import OrderedDict
from pydoc import locate


class SessionDatabase(Loadable):

    META_DATA_MAP = OrderedDict((
        ("channels", "biofb.hardware.Channel"),
        ("devices", "biofb.hardware.Device"),
        ("setups", "biofb.hardware.Setup"),
        ("subjects", "biofb.session.Subject"),
        ("controllers", "biofb.session.Controller"),
        ("locations", "biofb.session.Location"),
        ("settings", "biofb.session.Setting"),
    ))

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

                db = SessionDatabase(**{**db, **kwargs})

                for sample in db.samples:
                    sample.load_data()

                return db
        except FileNotFoundError as fnfe:
            if path.isabs(filename):
                raise fnfe

            return SessionDatabase.load(path.abspath(filename), **kwargs)

    @staticmethod
    def load_metadata(filename: str, meta_data_map: (dict, ) = None) -> (dict, list):
        """ Load """
        assert path.isfile(path.abspath(filename))
        meta_data = Loadable.load_dict_like(filename)
        meta_data = meta_data.get(['meta_data'], meta_data)  # try nested meta_data structure

        meta_data_evaluated = {}

        if meta_data_map is None:
            meta_data = SessionDatabase.META_DATA_MAP.items()

        for k, k_cls in meta_data_map:
            try:
                meta_data_cls = locate(k_cls) if not isinstance(k_cls, type) else k_cls

                assert hasattr(meta_data_cls, 'load')

                try:
                    v_list_of_dicts = meta_data[k]  # try nested meta_data structure
                except ValueError:
                    v_list_of_dicts = meta_data

                for v_dict in v_list_of_dicts:
                    v_cls = meta_data_cls.load(v_dict)
                    v_list = meta_data_evaluated.get(k, [])
                    v_list.append(v_cls)
                    meta_data_evaluated[k] = v_list

            except KeyError:
                pass

        return meta_data_evaluated

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

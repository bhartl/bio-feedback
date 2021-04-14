import yaml
import json
import os.path
import csv
import inspect
import h5py
import numpy as np


class Loadable(object):
    """ Loadable object via dict representation.

    The class provides methods to handle dict-like objects in general.

    **Note**: This class is envisaged to be a placeholder for a more involved database approach.
    """

    def __init__(self, *args, **kwargs):
        pass

    def to_dict(self):
        signature = inspect.signature(self.__init__)
        parameters = [p for p in signature.parameters]
        # defaults = [signature.parameters[p].default for p in parameters]

        # return {p: getattr(self, p)
        #         for p, d in zip(parameters, defaults)
        #         if getattr(self, p) is not d and getattr(self, p) != d}

        dict_repr = {}
        for p in parameters:
            try:
                v = getattr(self, p, getattr(self, '_'+p))
                if isinstance(v, Loadable):
                    v = v.to_dict()
                elif isinstance(v, list):
                    v = [
                        vi.to_dict() if isinstance(vi, Loadable) else vi
                        for vi in v
                    ]

                dict_repr[p] = v
            except AttributeError as ex:
                pass

        return dict_repr

    @classmethod
    def load(cls, value):
        """ Load Loadable instance based on dict-representation.

        :param value: dict-like representation of Loadable object to be loaded.
        :return: cls instance of provided dict-representation.
        """
        if value is None:
            return cls()

        if isinstance(value, cls):
            return value

        if not isinstance(value, dict):

            try:
                if not isinstance(value, tuple):
                    value = cls.load_dict_like(value)
                else:
                    # if tuple is provided, use as arguments
                    value = cls.load_dict_like(*value)
                    return cls.load(value)
            except AssertionError:

                # check, whether representation of dict or tuple has been passed via value
                v = value
                if isinstance(value, str):
                    value = eval(value)
                    assert not isinstance(value, str), f"Did not understand value `{v}` to load {cls} instance."

                return cls.load(value)

        return cls(**value)

    def dump(self, filename, file_format='yml', exist_ok=True):
        print(f'Export {self.__class__.__name__}-instance to file `{filename}`')

        sample_repr = self.to_dict()

        if not exist_ok:
            assert not os.path.isfile(filename), f"Specified file `{filename}` exists."

        os.makedirs(os.path.dirname(filename), exist_ok=True)

        if file_format.lower() in ('yml', 'yaml'):
            with open(filename, 'w') as outfile:
                yaml.safe_dump(sample_repr, outfile)
        elif file_format.lower() in ('json',):
            with open(filename, 'w') as outfile:
                json.dump(sample_repr, outfile)
        elif file_format.lower() in ('hdf5', 'h5', 'h5py'):
            with h5py.File(filename, 'w') as h5:
                sample_repr = {self.__class__.__name__: sample_repr}
                Loadable.recursively_save_dict_contents_to_group(h5, '/', sample_repr)
        else:
            raise NotImplementedError(f'file_format {file_format}')

    @staticmethod
    def recursively_save_dict_contents_to_group(h5, path, dict_repr):
        """
        ....
        """
        for k, v in dict_repr.items():
            path_k = path + k
            if isinstance(v, (list, tuple)):
                v = Loadable.list_to_dict(v)

            if isinstance(v, (np.ndarray, np.int64, np.float64, str, bytes, int, float)) or v is None:

                if v is None:
                    v = np.nan

                try:
                    h5[path_k] = v
                except OSError:
                    if path_k[-1] == ".":
                        path_k = path_k[:-1] + "'.'"
                        h5[path_k] = v

            elif isinstance(v, dict):
                Loadable.recursively_save_dict_contents_to_group(h5, path_k + '/', v)
            else:
                raise ValueError(f'Don\'t understand type {type(v)}.')

    @staticmethod
    def list_to_dict(list_instance):
        return {str(i): vi for i, vi in enumerate(list_instance)}

    @staticmethod
    def dict_to_list(dict_instance):
        integer_keyed = {int(k): v for k, v in dict_instance.items()}
        return list(integer_keyed)

    @classmethod
    def load_dict_like(cls, value: (str, dict), index=None) -> dict:
        """ Load dict-like object via provided value (path, yaml, json, repr, ...)

        :param value: Dict-like object or path to dict-like representation (path, yaml, json, repr, ...)
        :param index: (Optional) index of dict to load from list of dicts (e.g. form csv-file)
        :return: Dictionary representation of value
        """

        if value is None:
            return dict()

        loaded = None

        if isinstance(value, dict):
            loaded = value

        elif isinstance(value, str):
            if os.path.exists(value):
                try:
                    loaded = json.loads(value)
                except ValueError:
                    try:
                        with open(value, 'r') as s:
                            loaded = yaml.safe_load(s)

                        assert isinstance(loaded, dict) or isinstance(loaded, list)

                    except:
                        try:
                            with open(value, 'r') as s:
                                data = [line for line in csv.DictReader(s)]
                                if index is not None:
                                    loaded = data[index]
                                else:
                                    loaded = Loadable.list_of_dicts_to_dict_of_lists(data)
                        except:
                            with h5py.File(value, 'r') as h5:
                                loaded = Loadable.recursively_load_dict_contents_from_group(h5, '/')
            else:
                try:
                    loaded = json.loads(value)
                except ValueError:
                    try:
                        loaded = yaml.safe_load(value)
                    except Exception:
                        pass

        else:
            try:
                loaded = dict(value)
            except ValueError:
                pass

        assert isinstance(loaded, dict), f"Value must be either a dict-like object or a path to " \
                                         f"dict-like file (yml, json). Did not understand `{value}` " \
                                         f"of type `{type(value)}`."

        return loaded

    @staticmethod
    def recursively_load_dict_contents_from_group(h5, path):
        """
        ....
        """
        ans = {}
        for key, item in h5[path].items():
            if isinstance(item, h5py._hl.dataset.Dataset):
                ans[key] = item.value
            elif isinstance(item, h5py._hl.group.Group):
                ans[key] = Loadable.recursively_load_dict_contents_from_group(h5, path + key + '/')
        return ans

    @classmethod
    def load_dict_from_hdf5(cls, filename):
        """
        ....
        """
        with h5py.File(filename, 'r') as h5:
            return cls(Loadable.recursively_load_dict_contents_from_group(h5, '/'))

    @staticmethod
    def list_of_dicts_to_dict_of_lists(data: list):
        list_of_dicts = {}
        for k, v in [(key, d[key]) for d in data for key in d]:
            values = list_of_dicts.get(k, [])
            values.append(v)
            list_of_dicts[k] = values

        return list_of_dicts

    @staticmethod
    def dict_of_lists_to_list_of_dicts(data: dict):
        keys = list(data.keys())
        list_of_dicts = [
            {k: vi for k, vi in zip(keys, row_data)}
            for row_data in zip(*(data[k] for k in keys))
        ]
        return list_of_dicts

    @classmethod
    def from_terminal(cls, avoid=(), **defaults):
        signature = inspect.signature(cls.__init__)
        parameters = [p for p in signature.parameters if p not in avoid][1:]
        defaults = [defaults.get(p, signature.parameters[p].default) for p in parameters]

        dict_repr = {}
        for p, d in zip(parameters, defaults):
            value = input(f'{p}' + f' ({d})'*(d is not inspect._empty) + ': ')
            dict_repr[p] = value.strip() if value.strip() != '' else d

        return cls.load(dict_repr)

    @staticmethod
    def get_first_in(d, keys, lower=True, upper=True, exchangeable=(' ', '_', '-')):
        for key in keys:
            if key in d:
                return d[key]

            if lower and key.lower() in d:
                return d[key.lower()]

            if upper and key.upper() in d:
                return d[key.upper()]

            for exchange in exchangeable:
                for exchange_with in exchangeable:
                    if exchange == exchange_with:
                        continue

                    key = key.replace(exchange, exchange_with)
                    if key in d:
                        return d[key]

                    if lower and key.lower() in d:
                        return d[key.lower()]

                    if upper and key.upper() in d:
                        return d[key.upper()]

        raise KeyError(keys)

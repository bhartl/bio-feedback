import yaml
import json
import os.path
import csv
import inspect


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

        return {p: getattr(self, p) for p in parameters}

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
            value = cls.load_dict_like(value)

        return cls(**value)

    @classmethod
    def load_dict_like(cls, value: (str, dict)) -> dict:
        """ Load dict-like object via provided value (path, yaml, json, repr, ...)

        :param value: Dict-like object or path to dict-like representation (path, yaml, json, repr, ...)
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
                    except:
                        with open(value, 'r') as s:
                            data = [line for line in csv.DictReader(s)]
                            loaded = Loadable.list_of_dicts_to_dict_of_lists(data)
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
    def from_terminal(cls):
        signature = inspect.signature(cls.__init__)
        parameters = [p for p in signature.parameters][1:]
        defaults = [signature.parameters[p].default for p in parameters]

        dict_repr = {}
        for p, d in zip(parameters, defaults):
            value = input(f'{p} ({d}): ')
            dict_repr[p] = value

        return cls.load(dict_repr)

import yaml
import json
import os.path


class Loadable(object):
    """ Loadable object via dict representation.

    The class provides methods to handle dict-like objects in general.

    **Note**: This class is envisaged to be a placeholder for a more involved database approach.
    """

    def __init__(self, *args, **kwargs):
        pass

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
                with open(value, 'r') as s:
                    loaded = yaml.safe_load(s)

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

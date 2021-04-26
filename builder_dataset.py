from pandas import DataFrame
from collections.abc import MutableMapping


class DataSet(MutableMapping):
    """This class acts as a dict-like dataset that stores information.
    It takes a DataFrame object along with other fields.
    The frame is stored and if any of the other fields are names
    of columns within the frame, they are renamed to a proper form.
    If the other fields are not within the frame object, they are
    stored as attributes of the object.
    """

    def __init__(self, frame: DataFrame = None, **kwargs):
        self._store = {}
        self.frame: DataFrame = frame
        self._aliases = {}

        for item in kwargs.items():
            self.__setitem__(item[0], item[1])

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __getattr__(self, key):
        return self.__getitem__(key)

    def __getitem__(self, key):
        try:
            return self.__dict__[key]
        except KeyError:
            try:
                return self.__dict__['_store'][key]
            except KeyError:
                return self.__dict__['frame'][key]

    def __setitem__(self, key, value):
        try:
            if key in self._aliases:
                self.frame.rename({key: self._aliases[key]}, axis=1, inplace=True, errors='raise')
            self.frame.rename({value: key}, axis=1, inplace=True, errors='raise')
            self._aliases[key] = value
        except (TypeError, AttributeError, KeyError):
            if key in ['_aliases', '_store']:
                self.__dict__[key] = value
            else:
                self._store[key] = value

    def __delitem__(self, v):
        del self._store[v]

    def __len__(self):
        return len(self._store)

    def __iter__(self):
        return iter(self._store)

    def __str__(self):
        return str(self._store)

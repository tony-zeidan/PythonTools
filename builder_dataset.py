from pandas import DataFrame


class BuilderDataSet:
    """This class acts as a dict-like dataset that stores information.

    It takes a DataFrame object along with other fields.
    The frame is stored and if any of the other fields are names
    of columns within the frame, they are renamed to a proper form.
    If the other fields are not within the frame object, they are
    stored as attributes of the object.
    """

    def __init__(self, frame: DataFrame = None, **kwargs):
        self.frame: DataFrame = frame
        self._aliases = {}
        for item in kwargs.items():
            self.__setitem__(item[0], item[1])

    def __setattr__(self, key, value):
        try:
            self.__setitem__(key, value)
        except KeyError:
            object.__setattr__(self, key, value)

    def __getattr__(self, key):
        return self.__getitem__(key)

    def __getitem__(self, key):
        try:
            return self.__dict__[key]
        except KeyError:
            return self.__dict__['frame'][key]

    def __setitem__(self, key, value):
        try:
            if key in self._aliases:
                self.frame.rename({key: self._aliases[key]}, axis=1, inplace=True, errors='raise')
            self.frame.rename({value: key}, axis=1, inplace=True, errors='raise')
            self._aliases[key] = value
        except (TypeError, AttributeError):
            self.__dict__[key] = value

# create exceptions and error classes
from .helpers import err_to_exception


class QErrorNoneAvailable(NotImplementedError):
    pass


class QErrorWrongArgument(ValueError):
    pass


class kCGErrorTypes(IOError):  # noqa
    """
        Universal type for associations error codes added.
       .. versionadded:: 0.0.1
    """
    def __init__(self, n):
        self.n = n
        pass

    def __repr__(self):
        return self.n

    def err(self):
        return err_to_exception(self.n)


class DictionaryKeys:
    def __init__(self, d):
        self.dictionary = d

    def __getattr__(self, item):
        return self.dictionary[item]


class SelectedWindow:
    """
     A class representing a selected windows in the current user session.
    This class encapsulates the information of a window retrieved from the macOS window session.
    """
    def __repr__(self):
        return (f'<{SelectedWindow.__name__} with constants ' +
                ';\n\t'.join(self.nsdict) + ';>')

    def __init__(self, nsdict):
        self.nsdict = nsdict
        for key, value in nsdict.items():
            setattr(self, key, value)  # set the available keys of data as
                                       # attributes to reverted SelectedWindow class
    def __getattr__(self, attr):
        pass

    def __getitem__(self, _index):
        return self.nsdict[_index]
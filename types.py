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

    def err(self):
        return err_to_exception(self.n)

# create exceptions and error classes


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
        pass

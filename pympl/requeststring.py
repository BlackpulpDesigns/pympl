from pympl.types import encode_value


class RequestString(dict):
    """
    A simple class for creating properly-encoded Ministry Platform request
    strings. This is really just a standard :class:`dict` with a custom
    ``__str__()`` method, which farms out the encoding.
    """
    def __str__(self):
        result = []

        for key, value in self.iteritems():
            result.append('%s=%s' % (key, encode_value(value)))

        return '&'.join(result)

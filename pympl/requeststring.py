from pympl.types import encode_value


class RequestString(dict):
    def __str__(self):
        result = []

        for key, value in self.iteritems():
            result.append('%s=%s' % (key, encode_value(value)))

        return '&'.join(result)
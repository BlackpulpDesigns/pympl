from datetime import datetime, date
from decimal import Decimal
from dateutil.parser import parse as parse_date
import uuid


class DateTime(object):
    def encode(self, value):
        return value.strftime('%Y-%m-%d %I:%M:%S %p') if value else ''

    def decode(self, value):
        return parse_date(value) if value else None


class Date(object):
    def encode(self, value):
        return value.strftime('%Y-%m-%d') if value else ''

    def decode(self, value):
        return parse_date(value).date() if value else None


class String(object):
    def encode(self, value):
        return value\
            .replace('&', 'dp_Amp')\
            .replace('=', 'dp_Equal')\
            .replace('#', 'dp_Pound')\
            .replace('?', 'dp_Qmark')

    def decode(self, value):
        return value


class Integer(object):
    def encode(self, value):
        return str(int(value)) if value is not None else ''

    def decode(self, value):
        return int(value) if value else None


class Float(object):
    def encode(self, value):
        return str(float(value)) if value is not None else ''

    def decode(self, value):
        return float(value) if value else None


class Numeric(object):
    def encode(self, value):
        return str(Decimal(value)) if value is not None else ''

    def decode(self, value):
        return Decimal(value) if value else None


class Boolean(object):
    def encode(self, value):
        return '' if value is None else v == 1 or v == 'true'

    def decode(self, value):
        return value == 'true' or value == '1'


class Null(object):
    def encode(self, value):
        return ''

    def decode(self, value):
        return None


class Uuid(object):
    def encode(self, value):
        return str(value) if value else ''

    def decode(self, value):
        return uuid.UUID(value) if value else None


DATETIME = DateTime()
STRING = String()
INTEGER = Integer()
FLOAT = Float()
NUMERIC = Numeric()
BOOLEAN = Boolean()
NULL = Null()
UUID = Uuid()


def encode_value(value):
    encoding_map = {
        datetime: DATETIME,
        str: STRING,
        int: INTEGER,
        bool: BOOLEAN,
        float: FLOAT,
        type(None): NULL,
        uuid.UUID: UUID
    }

    if type(value) in encoding_map:
        return encoding_map[type(value)].encode(value)

    return STRING.encode(value)


all_types = {
    'int': INTEGER,
    'string': STRING,
    'boolean': BOOLEAN,
    'dateTime': DATETIME,
    'date': STRING,
    'bit': INTEGER,
    'smallint': INTEGER,
    'bigint': INTEGER,
    'tinyint': INTEGER,
    'money': FLOAT,
    'numeric': NUMERIC,
    'short': INTEGER,
    'long': INTEGER,
    'float': FLOAT,
    'unsignedByte': INTEGER,
    'decimal': NUMERIC,
    'varchar': STRING,
    'text': STRING,
    'uniqueidentifier': UUID,
    'nvarchar': STRING,
    'binary': STRING,
    'time': STRING,
    'datetime': DATETIME,
    'base64Binary': STRING
}
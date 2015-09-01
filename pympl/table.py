import inflect
from pympl.requeststring import RequestString


_inflect_engine = inflect.engine()


def _derive_primary_key_from_table_name(name):
    words = name.lstrip('dp_').split('_')
    first_words = words[:-1]
    last_word = words[-1]
    singular = _inflect_engine.singular_noun(last_word)
    if not singular:
        singular = last_word
    pk = first_words + [singular, 'ID']
    return '_'.join(pk)


class Table(object):
    def __init__(self, client, name, primary_key=None):
        self.client = client
        self.name = name
        self.primary_key = (
            primary_key or _derive_primary_key_from_table_name(name)
        )

    def __call__(self, *args, **kwargs):
        return self.record(*args, **kwargs)

    def __repr__(self):
        return "<Table(%s, primary_key=%s)>" % (self.name, self.primary_key)

    def record(self, *args, **initial_data):
        return Record(self, *args, **initial_data)


class Record(dict):
    def __init__(self, table, initial_data):
        self.table = table
        dict.__init__(self, initial_data)

    def __repr__(self):
        return "<Record(%s, %s=%s)>" % (
            self.table.name, self.table.primary_key,
            self.get(self.table.primary_key)
        )

    def as_request_string(self):
        return RequestString(self)

    def save(self, user_id=None):
        final_user_id = (
            user_id if user_id is not None else
            self.table.client.user_id
        )

        if self.new:
            response = self.table.client.fn.AddRecord(
                TableName=self.table.name,
                PrimaryKeyField=self.table.primary_key,
                RequestString=str(self.as_request_string()),
                UserID=final_user_id
            )

            # Add the newly-minited ID to the record
            self[self.table.primary_key] = response[0]

        else:
            response = self.table.client.fn.UpdateRecord(
                TableName=self.table.name,
                PrimaryKeyField=self.table.primary_key,
                RequestString=str(self.as_request_string()),
                UserID=final_user_id
            )

        return response

    @property
    def new(self):
        return not bool(self.get(self.table.primary_key))


class TableFactory(object):
    def __init__(self, client):
        self.client = client

    def __getitem__(self, key):
        if isinstance(key, tuple) and len(key) == 2:
            return Table(self.client, key[0], primary_key=key[1])
        return Table(self.client, key)

    def __getattr__(self, key):
        return Table(self.client, key)

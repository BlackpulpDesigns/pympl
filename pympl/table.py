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
    """
    Table objects are a simple abstraction that sit on top of pympl's SOAP
    function interface. They facilitate interacting with tables and records
    more akin to what you'd expect from an ORM.

    To instantiate a table object, you should use the ``Client`` object's
    ``table`` attribute, as this is an instance of
    :class:`TableFactory <pympl.table.TableFactory>`. Accessing any
    attribute on the ``TableFactory`` will create a ``Table`` object with that
    attribute's name. By default, the primary key field is guessed by taking
    the singular form of the last word of the table's name and appending
    ``_ID`` to it.

    For example, if we wanted to get an ``Table`` object for the Contacts
    table, we can simply do::

        Contacts = client.table.Contacts

    This will return a ``Table`` object with the primary key field
    ``Contact_ID``.

    If the primary key for the table does not follow this convention, you may
    specify it manually like so::

        Some_Table = client.table['Some_Table', 'Some_Table_ID']

    Once a ``Table`` object is acquired, :class:`Record <pympl.table.Record>`
    objects can be created by either calling the ``Table`` object or by
    calling the ``Table`` object's ``record()`` method::

        record = client.table.Contacts(First_Name='Bob')
        # or, alternatively:
        record2 = client.table.Contacts.record(First_Name='Bob')
    """
    def __init__(self, client, name, primary_key=None):
        self.client = client
        self.name = name
        self.primary_key = (
            primary_key or _derive_primary_key_from_table_name(name)
        )

    def __call__(self, *args, **kwargs):
        """
        Creates a new :class:`Record <pympl.table.Record>` object. Any
        keyword arguments passed will be used to initialize the record object
        with data.

        This is calls :meth:`Table.record() <pympl.table.Table.record>`
        internally.

        :return: A new record
        :rtype: :class:`Record <pympl.table.Record>`
        """
        return self.record(*args, **kwargs)

    def __repr__(self):
        return "<Table(%s, primary_key=%s)>" % (self.name, self.primary_key)

    def record(self, *args, **initial_data):
        """
        See documentation for
        :meth:`Table.__call__() <pympl.table.Table.__call__>`.
        """
        return Record(self, *args, **initial_data)


class Record(dict):
    """
    Provides an ORM-like interface to Ministry Platform records. These objects
    should almost always be instantiated by utilizing a ``Table`` object,
    generated via :attr:`pympl.Client.table`.
    """
    def __init__(self, table, initial_data):
        self.table = table
        dict.__init__(self, initial_data)

    def __repr__(self):
        return "<Record(%s, %s=%s)>" % (
            self.table.name, self.table.primary_key,
            self.get(self.table.primary_key)
        )

    def as_request_string(self):
        """
        Returns the data as a :class:`pympl.RequestString` object.
        """
        return RequestString(self)

    def save(self, user_id=None):
        """
        Saves the record to the database. If the record is "new", then
        ``AddRecord`` is called; otherwise, ``UpdateRecord`` is.

        :param int user_id: Optionally, one can specify which user should be
            used for the add/update operation. If none is provided, the user
            ID provided to the ``Client`` on initialization will be used
            (if any).

        :return: The response from the database.
        :rtype: tuple
        :raises pympl.exc.AddRecordError: If new and operation fails.
        :raises pympl.exc.UpdateRecordError: If not new and operation fails.
        """
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
        """
        Whether or not the record all ready has a home in Ministry Platform or
        not. This is determined by checking if the table's primary key field
        exists in the record and is truthy.
        """
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

from pympl.requeststring import RequestString
from pympl.resolvers import SchemaResolver
import pympl.exc as exc
from suds.sax.text import Text
from datetime import date


_functions = {}


def _make_request_string(string):
    if string:
        return (
            string if isinstance(string, basestring) else
            str(RequestString(string))
        )
    return ''


class FunctionMeta(type):
    def __init__(cls, name, bases, dict_):
        if name != 'Function':
            _functions[name] = cls
        type.__init__(cls, name, bases, dict_)


class Function(object):
    """
    The base Function class that all of the others inherit from.
    """
    __metaclass__ = FunctionMeta

    _signature = tuple()

    def __init__(self, client):
        self.client = client

    def __call__(self, *args, **kwargs):
        """
        A simple helper to make the function request and immediately return
        the result of its ``call()`` method.

        This allows us to do things like::

            # Get the function object
            AuthenticateUser = client.fn.AuthenticateUser

            # Now call it with the requested parameters
            response = AuthenticateUser('username', 'password')

        This is short hand for::

            request = client.fn.AuthenticateUser.make_request(
                'username', 'password')
            response = request.call()
        """
        request = self.make_request(*args, **kwargs)
        return request.call()

    def __repr__(self):
        return "<pymple.function.%s>" % type(self).__name__

    def make_request(self, *args, **kwargs):
        """
        Creates and returns a request object for the function. This method is
        often overridden by specific functions to augment behavior.

        :return: The request
        :rtype: :class:`FunctionRequest <pympl.function.FunctionRequest>`
        """
        return FunctionRequest(self, args, kwargs)

    def _prepare_args(self, args, kwargs):
        all_kwargs = kwargs.copy()
        all_kwargs.update(self._prefill_args())
        result = (self._encode_args(args), self._encode_kwargs(all_kwargs))
        return result

    def _encode_args(self, args):
        encoded_args = []

        for i, arg in enumerate(args):
            encoded_args.append(
                '' if arg is None else self._signature[i][1](arg))

        return encoded_args

    def _encode_kwargs(self, kwargs):
        encoded_kwargs = {}

        for (arg, type_) in self._signature:
            if arg in kwargs:
                encoded_kwargs[arg] = (
                    '' if kwargs[arg] is None else
                    type_(kwargs[arg])
                )

        return encoded_kwargs


class GuidPasswordPrefill(object):
    def _prefill_args(self):
        return {
            'GUID': self.client.guid,
            'Password': self.client.password
        }


class FunctionRequest(object):
    """
    A simple object that binds the function being called with the arguments
    that are to be passed to that function when it is called.

    This class is also responsible for creating the appropriate response, upon
    completion of the request. By default, the response is parsed to a
    standard :class:`dict`. However, some functions return subclassed
    ``FunctionRequest`` which in turn parse responses into various other
    types of objects.
    """
    def __init__(self, function, args, kwargs):
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        return "<pymple.function.%s>" % type(self).__name__

    def call(self):
        """
        Parses arguments and calls the underlying Ministry Platform SOAP
        function.
        """
        function_name = type(self.function).__name__
        function = getattr(self.function.client._suds.service, function_name)
        prepped_args = self.function._prepare_args(self.args, self.kwargs)
        return self._parse_response(
            function(*prepped_args[0], **prepped_args[1])
        )

    def _parse_response(self, response):
        result = self.function.client._suds.dict(response)
        for key, value in result.iteritems():
            if isinstance(value, Text):
                result[key] = str(value)
        return result


class AddRecord(Function):
    """
    Adds a record to a Ministry Platform table. Please note that it's
    generally easier to use the :obj:`pympl.Client.table` attribute to access
    a table object and create/update records via that mechanism.
    """
    _signature = (
        ('GUID', str),
        ('Password', str),
        ('UserID', int),
        ('TableName', str),
        ('PrimaryKeyField', str),
        ('RequestString', _make_request_string)
    )

    def _prefill_args(self):
        return {
            'GUID': self.client.guid,
            'Password': self.client.password,
            'UserID': self.client.user_id
        }

    def make_request(self, *args, **kwargs):
        """
        :param str TableName: The name of the Ministry Platform table to add a
           record to.

        :param str PrimaryKeyField: The primary key field name of the table that
           you want to add a record to. This is typically the singular form of
           the table name, suffixed with ``_ID``. For example, if you wanted to
           add a record to the ``Contacts`` table, the primary key field would
           be ``Contact_ID``.

        :param str|dict|RequestString RequestString: Either an instance of
           :class:`pympl.RequestString` or a manually-formatted Ministry
           Platform request string. See the Ministry Platform documentation on
           request strings if you want to perform the formatting yourself.
           Alternatively, you can also pass a :class:`dict` as the request
           string and it will be converted to a ``RequestString`` object and
           used that way.

        :return: A new request object, which can be used to query the Ministry
           Platform API.

        :rtype: :class:`AddRecordRequest <pympl.function.AddRecordRequest>`
        """
        return AddRecordRequest(self, args, kwargs)


class AddRecordRequest(FunctionRequest):
    """
    Parses the response into a tuple, if the request succeeds:
    ``(record_id, 0, message)``.
    """
    def _parse_response(self, response):
        id_, junk, message = str(response).split('|', 2)
        if id_ == '0':
            raise exc.AddRecordError(message.lstrip('Exception: '))
        return (int(id_), int(junk), message)


class UpdateRecord(Function):
    """
    Like :class:`AddRecord <pympl.function.AddRecord>` but updates instead.
    """
    _signature = (
        ('GUID', str),
        ('Password', str),
        ('UserID', int),
        ('TableName', str),
        ('PrimaryKeyField', str),
        ('RequestString', _make_request_string)
    )

    def _prefill_args(self):
        return {
            'GUID': self.client.guid,
            'Password': self.client.password,
            'UserID': self.client.user_id
        }

    def make_request(self, *args, **kwargs):
        """
        :param str TableName: The name of the Ministry Platform table to add a
           record to.

        :param str PrimaryKeyField: The primary key field name of the table that
           you want to add a record to. This is typically the singular form of
           the table name, suffixed with ``_ID``. For example, if you wanted to
           add a record to the ``Contacts`` table, the primary key field would
           be ``Contact_ID``.

        :param str|dict|RequestString RequestString: Either an instance of
           :class:`pympl.RequestString` or a manually-formatted Ministry
           Platform request string. See the Ministry Platform documentation on
           request strings if you want to perform the formatting yourself.
           Alternatively, you can also pass a :class:`dict` as the request
           string and it will be converted to a ``RequestString`` object and
           used that way.

        :return: A new request object, which can be used to query the Ministry
           Platform API
        :rtype: :class:`UpdateRecordRequest
           <pympl.function.UpdateRecordRequest>`
        """
        return UpdateRecordRequest(self, args, kwargs)


class UpdateRecordRequest(FunctionRequest):
    """
    Virtually identical to :class:`pympl.function.AddRecordRequest`.
    """
    def _parse_response(self, response):
        id_, junk, message = str(response).split('|', 2)
        if id_ == '0':
            raise exc.UpdateRecordError(message.lstrip('Exception: '))
        return (int(id_), int(junk), message)


class AuthenticateUser(Function):
    """
    Calls the MP SOAP function 'AuthenticateUser'. This is a common way to
    validate a user's credentials and check for basic authorization.

    For example, one might want to do something like this::

        user_info = client.fn.AuthenticateUser('username', 'password')
        user_info['CanImpersonate']
        user_info['UserID']

    .. method:: make_request(*args, **kwargs)

       :param str UserName: The user name to check.
       :param str Password: The password to check.
       :return: The function request object
       :rtype: :class:`FunctionRequest <pympl.function.FunctionRequest>`
    """
    _signature = (
        ('UserName', str),
        ('Password', str),
        ('ServerName', str)
    )

    def _prefill_args(self):
        return {
            'ServerName': self.client.server_name
        }


class GetUserInfo(Function):
    """
    Gets information about the requested user ID. The response from the
    server is returned as a
    :class:`GetUserInfoResponse <pympl.function.GetUserInfoResponse>`.

    Example::

        user_info = client.fn.GetUserInfo(UserID=234)
        user_info.contact   # A Contact table object for the user
        user_info.user  # A User table object for the user
    """
    _signature = (
        ('GUID', str),
        ('Password', str),
        ('UserID', int)
    )

    def _prefill_args(self):
        return {
            'GUID': self.client.guid,
            'Password': self.client.password
        }

    def make_request(self, *args, **kwargs):
        """
        :param int UserID: The user ID to look up.

        :return: The function request object.
        :rtype: :class:`GetUserInfoRequest <pympl.function.GetUserInfoRequest>`
        """
        return GetUserInfoRequest(self, args, kwargs)


class GetUserInfoRequest(FunctionRequest):
    """
    A simple ``FunctionRequest`` object that returns a
    :class:`GetUserInfoResponse <pympl.function.GetUserInfoResponse>`
    object, upon response parsing.
    """
    def _parse_response(self, response):
        return GetUserInfoResponse(self, response)


class GetUserInfoResponse(object):
    """
    Aggregates all of the data from ``GetUserInfo`` API call and dumps it into
    easy-to-use objects.

    .. attribute:: request

       The function request object.

    .. attribute:: raw

       The raw response XML.

    .. attribute:: contact

       A ``Contacts`` :class:`Table <pympl.table.Table>` object instantiated
       with the user's contact record data.

    .. attribute:: user

       A ``dp_Users`` :class:`Table <pympl.table.Table>` object instantiated
       with the user's user record data.

    .. attribute:: prefixes

       A :class:`list` of name prefixes from Ministry Platform.

       Example::

         [{'Prefix': 'Mr.', 'Prefix_ID': 1}, {'Prefix': 'Mrs.', 'Prefix_ID': 2}, ... ]

    .. attribute:: suffixes

       A :class:`list` of name suffixes from Ministry Platform.

       Example::

         [{'Suffix_ID': 1, 'Suffix': 'Jr.'}, {'Suffix_ID': 2, 'Suffix': 'Sr.'}, ... ]

    .. attribute:: genders

       A :class:`list` of genders from Ministry Platform.

       Example::

         [{'Gender_ID': 1, 'Gender': 'Male'}, {'Gender_ID': 2, 'Gender': 'Female'}]

    .. attribute:: marital_statuses

       A :class:`list` of marital satuses from Ministry Platform.

       Example::

         [
           {'Marital_Status': 'Single', 'Marital_Status_ID': 1},
           {'Marital_Status': 'Married', 'Marital_Status_ID': 2},
           ...
         ]
    """
    def __init__(self, request, response):
        self.request = request
        self.raw = response
        self._resolver = SchemaResolver(response.schema, response.diffgram)

        # Create some funsies
        self.contact = request.function.client.table.Contacts(
            self._resolver.Table.first())
        self.user = request.function.client.table.dp_User(
            self._resolver.Table1.first())
        self.prefixes = self._resolver.Table2
        self.suffixes = self._resolver.Table3
        self.genders = self._resolver.Table4
        self.marital_statuses = self._resolver.Table5

    def __repr__(self):
        return "<pymple.function.GetUserInfoResponse(%s)>" % (
            self.user.get('User_Name')
        )


def _encode_file_contents(obj):
    if hasattr(obj, 'read'):
        return obj.read().encode('base64')
    else:
        return obj.encode('base64')


class AttachFile(Function):
    """
    Attaches a file to a Ministry Platform record.

    For example::

        file_guid, error_code, message = client.fn.AttachFile(
            FileContents=open('/path/to/file.jpg'),
            FileName='myfile.jpg',
            PageID=23,
            RecordID=798,
            FileDescription='A picture of a thing',
            IsImage=True,
            ResizeLongestDimension=0  # Don't resize the image
        )
    """
    _signature = (
        ('GUID', str),
        ('Password', str),
        ('FileContents', _encode_file_contents),
        ('FileName', str),
        ('PageID', int),
        ('RecordID', int),
        ('FileDescription', str),
        ('IsImage', bool),
        ('ResizeLongestDimension', int)
    )

    def _prefill_args(self):
        return {
            'GUID': self.client.guid,
            'Password': self.client.password,
            'ResizeLongestDimension': 0
        }

    def make_request(self, *args, **kwargs):
        """
        :param file FileContents: The file object to send to Ministry Platform.
        :param str FileName: The name of the file.
        :param int PageID: The page ID that the record belongs to.
        :param int RecordID: The record ID that you want to attach the file to.
        :param str FileDescription: A description of the file.
        :param bool IsImage: Whether or not the file is an image.
        :param int ResizeLongestDimension: The maximum size, in pixels, of an
            image's longest side. Set to ``0`` to disable resize.

        :return: The function request object
        :rtype: :class:`AttachFileRequest <pympl.function.AttachFileRequest>`
        """
        return AttachFileRequest(self, args, kwargs)


class AttachFileRequest(FunctionRequest):
    """
    A simple function request that parsers the string response into a
    convenient tuple: ``(guid, error_code, message)``.
    """
    def _parse_response(self, response):
        guid, junk, message = str(response).split('|', 2)
        return guid, int(junk), message


class UpdateDefaultImage(Function, GuidPasswordPrefill):
    _signature = (
        ('GUID', str),
        ('Password', str),
        ('PageID', int),
        ('RecordID', int),
        ('UniqueName', str)
    )

    def make_request(self, *args, **kwargs):
        return UpdateDefaultImageRequest(self, args, kwargs)


class UpdateDefaultImageRequest(FunctionRequest):
    def _parse_response(self, response):
        guid, junk, message = str(response).split('|', 2)
        if guid == '0':
            raise exc.UpdateDefaultImageError(message)
        return guid, int(junk), message


class ExecuteStoredProcedure(Function, GuidPasswordPrefill):
    """
    Executes a stored procedure on the Ministry Platform MSSQL Server
    instance.

    NOTE: The :attr:`pympl.client.Client.sp` attribute is the preferred method
    of executing stored procedures.
    """
    _signature = (
        ('GUID', str),
        ('Password', str),
        ('StoredProcedureName', str),
        ('RequestString', _make_request_string)
    )

    def make_request(self, *args, **kwargs):
        """
        :param str StoredProcedureName: The name of the stored procedure to
            execute. Only stored procedures that begin with ``api`` can be
            called.
        :param str|dict|RequestString RequestString: The parameters to pass
            to the stored procedure.

        :return: The function request object
        :rtype: :class:`ExecuteStoredProcedureRequest <pympl.function.ExecuteStoredProcedureRequest>`
        """
        return ExecuteStoredProcedureRequest(self, args, kwargs)


class ExecuteStoredProcedureRequest(FunctionRequest):
    """
    The function request for stored procedures. Parses the API response into
    an instance of
    :class:`ExecuteStoredProcedureResponse <pympl.function.ExecuteStoredProcedureResponse>`.
    """
    def _parse_response(self, response):
        return ExecuteStoredProcedureResponse(self, response)

    def __repr__(self):
        return "<pymple.function.ExecuteStoredProcedureRequest(%s)>" % (
            self.kwargs.get('StoredProcedureName', 'N/A')
        )


class ExecuteStoredProcedureResponse(object):
    """
    Contains all of the table information returned by a stored procedure call.
    This object can be iterated over, which yields each of the response
    tables. In addition, each table can be accessed via attributes on the
    object, e.g. ``response.table``, ``response.table2``, ``response.table3``.
    """
    def __init__(self, request, response):
        self.request = request
        self.raw = response
        self._resolver = SchemaResolver(response.schema, response.diffgram)

        for i in self._resolver.tables:
            setattr(self, i.lower(), getattr(self._resolver, i))

    def __repr__(self):
        return "<pymple.function.ExecuteStoredProcedureResponse(%s)>" % (
            self.request.kwargs.get('StoredProcedureName', 'N/A')
        )

    def __iter__(self):
        for i in self._resolver.tables:
            yield getattr(self._resolver, i)

    def as_dict(self):
        """
        Converts the response tables as a dictionary.

        :return: The stored procedure response.
        :rtype: dict
        """
        result = {}
        for i in self._resolver.tables:
            result[i] = getattr(self._resolver, i)
        return result


class FindOrCreateUserAccount(Function, GuidPasswordPrefill):
    _signature = (
        ('GUID', str),
        ('Password', str),
        ('FirstName', str),
        ('LastName', str),
        ('MobilePhone', str),
        ('EmailAddress', str)
    )


class UpdateUserAccount(Function, GuidPasswordPrefill):
    _signature = (
        ('GUID', str),
        ('Password', str),
        ('UserID', int),
        ('FirstName', str),
        ('LastName', str),
        ('MobilePhone', str),
        ('EmailAddress', str),
        ('NewPassword', str),
        ('MiddleName', str),
        ('NickName', str),
        ('PrefixID', int),
        ('SuffixID', int),
        ('DOB', lambda x: x.strftime('%Y-%m-%d') if x else ''),
        ('GenderID', int),
        ('MaritalStatusID', int)
    )

    def make_request(self, *args, **kwargs):
        return UpdateUserAccountRequest(self, args, kwargs)


class UpdateUserAccountRequest(FunctionRequest):
    def _parse_response(self, response):
        id_, junk, message = str(response).split('|', 2)
        if id_ == '0':
            raise exc.UpdateUserAccountError(message.lstrip('Exception: '))
        return int(id_), int(junk), message


class ResetPassword(Function, GuidPasswordPrefill):
    _signature = (
        ('GUID', str),
        ('Password', str),
        ('FirstName', str),
        ('EmailAddress', str)
    )

    def make_request(self, *args, **kwargs):
        return ResetPasswordRequest(self, args, kwargs)


class ResetPasswordRequest(FunctionRequest):
    def _parse_response(self, response):
        parsed_response = FunctionRequest._parse_response(self, response)
        id_, junk, message = str(
            parsed_response['ResetPasswordResult']).split('|', 2)
        if id_ == '0':
            raise exc.ResetPasswordError(message.lstrip('Exception: '))
        return parsed_response


class FunctionRegistry(object):
    """
    A simple object that facilitates instantiating function objects. Accessing
    an attribute of the function registry will return an instantiated function
    object, which can be used to query Ministry Platform::

      # A function registry is always instantiated at Client.fn
      function_instance = client.fn.AuthenticateUser

    Functions are callables. Calling them will call Ministry Platform with
    the parameters specified::

      response = function_instance('username', 'password')

    For specific information about the various functions, the parameters
    they receive and the objects they return, please reference the various
    ``Function`` class docs:

    * :class:`AddRecord <pympl.function.AddRecord>`
    * :class:`UpdateRecord <pympl.function.UpdateRecord>`
    * :class:`AuthenticateUser <pympl.function.AuthenticateUser>`
    * :class:`GetUserInfo <pympl.function.GetUserInfo>`
    * :class:`AttachFile <pympl.function.AttachFile>`
    * :class:`UpdateDefaultImage <pympl.function.UpdateDefaultImage>`
    * :class:`ExecuteStoredProcedure <pympl.function.ExecuteStoredProcedure>`
    * :class:`FindOrCreateUserAccount <pympl.function.FindOrCreateUserAccount>`
    * :class:`UpdateUserAccount <pympl.function.UpdateUserAccount>`
    * :class:`ResetPassword <pympl.function.ResetPassword>`
    """
    _cache = {}

    def __init__(self, client):
        self.client = client

    def __getattr__(self, name):
        if name not in self._cache:
            try:
                self._cache[name] = _functions[name](self.client)
            except KeyError:
                raise AttributeError(name)
        return self._cache[name]

    def __repr__(self):
        return "<pymple.function.FunctionRegistry>"

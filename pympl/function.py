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
    __metaclass__ = FunctionMeta

    _signature = tuple()

    def __init__(self, client):
        self.client = client

    def __call__(self, *args, **kwargs):
        request = self.make_request(*args, **kwargs)
        return request.call()

    def __repr__(self):
        return "<pymple.function.%s>" % type(self).__name__

    def make_request(self, *args, **kwargs):
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
    def __init__(self, function, args, kwargs):
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        return "<pymple.function.%s>" % type(self).__name__

    def call(self):
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
        return AddRecordRequest(self, args, kwargs)


class AddRecordRequest(FunctionRequest):
    def _parse_response(self, response):
        id_, junk, message = str(response).split('|', 2)
        if id_ == '0':
            raise exc.AddRecordError(message.lstrip('Exception: '))
        return (int(id_), int(junk), message)


class UpdateRecord(Function):
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
        return UpdateRecordRequest(self, args, kwargs)


class UpdateRecordRequest(FunctionRequest):
    def _parse_response(self, response):
        id_, junk, message = str(response).split('|', 2)
        if id_ == '0':
            raise exc.UpdateRecordError(message.lstrip('Exception: '))
        return (int(id_), int(junk), message)


class AuthenticateUser(Function):
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
        return GetUserInfoRequest(self, args, kwargs)


class GetUserInfoRequest(FunctionRequest):
    def _parse_response(self, response):
        return GetUserInfoResponse(self, response)


class GetUserInfoResponse(object):
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
        return AttachFileRequest(self, args, kwargs)


class AttachFileRequest(FunctionRequest):
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
    _signature = (
        ('GUID', str),
        ('Password', str),
        ('StoredProcedureName', str),
        ('RequestString', _make_request_string)
    )

    def make_request(self, *args, **kwargs):
        return ExecuteStoredProcedureRequest(self, args, kwargs)


class ExecuteStoredProcedureRequest(FunctionRequest):
    def _parse_response(self, response):
        return ExecuteStoredProcedureResponse(self, response)

    def __repr__(self):
        return "<pymple.function.ExecuteStoredProcedureRequest(%s)>" % (
            self.kwargs.get('StoredProcedureName', 'N/A')
        )


class ExecuteStoredProcedureResponse(object):
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
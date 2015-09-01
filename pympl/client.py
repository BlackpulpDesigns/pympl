import os
from suds.xsd.doctor import Import, ImportDoctor
from suds.client import Client as SudsClient
from pympl.function import FunctionRegistry
from pympl.storedproc import StoredProcedureFactory
from pympl.table import TableFactory

try:
    from configparser import SafeConfigParser as ConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser as ConfigParser


def _init_suds(wsdl):
    imp = Import('http://www.w3.org/2001/XMLSchema')
    imp.filter.add('http://thinkministry.com/')
    return SudsClient(wsdl, plugins=[ImportDoctor(imp)])


def _load_config_file():
    config = ConfigParser()
    config.read(['.pympl', os.path.expanduser('~/.pympl')])
    return config


class Client(object):
    """
    The central object for interacting with a specific Ministry Platform
    server. Clients can be instantiated in the traditional pattern, such as::

      client = Client('https://path/to/wsdl', guid, password, server_name)

    Or, alternatively, you can place a `.pympl` file in your application's
    directory and specify configuration parameters in that. This file is INI
    formatted. An example looks like:

    .. code-block:: ini

       [pympl]
       wsgi = http://path/to/wsdl
       guid = your_guid
       password = your_password
       server_name = your_server_name

    If a ``.pympl`` file is found upon ``Client`` instantiation, it will be
    used for fallback parameters. This allows you to instantiate the client
    more simply::

      client = Client()

    :param str wsdl: The URL of the Ministry Platform WSDL.
    :param str guid: The Ministry Platform API GUID to connect with.
    :param str password: The API password to use.
    :param str server_name: The name of the Ministry Platform server.
    :param int user_id: The default user ID to use for API calls.


    .. attribute:: fn

       An instance of :class:`pympl.function.FunctionRegistry`. This object
       is used for initiating Ministry Platform SOAP function calls. For
       example, if one wants to call the MP function `AuthenticateUser`, the
       following can be done::

         response = client.fn.AuthenticateUser('username', 'password')

       In the instance of `AuthenticateUser`, a dictionary will be returned.
       Or, if an error occurred, a :class:`pympl.exc.FunctionError`
       will be thrown.
    """
    def __init__(
            self, wsdl=None, guid=None, password=None, server_name=None,
            user_id=0, params=None):
        self._config_file = _load_config_file()

        #: The URL of the WSDL
        self.wsdl = wsdl or self._config_file.get('pympl', 'wsdl')
        self.guid = guid or self._config_file.get('pympl', 'guid')
        self.password = password or self._config_file.get('pympl', 'password')
        self.server_name = server_name or self._config_file.get(
            'pympl', 'server_name')
        self.user_id = user_id
        self.params = params or {
            'trace': True,
            'exceptions': 1
        }

        # Instantiate the suds client
        self._suds = _init_suds(self.wsdl)

        self.fn = FunctionRegistry(self)
        self.sp = StoredProcedureFactory(self)
        self.table = TableFactory(self)

    def __repr__(self):
        return "<pympl.Client(%s)>" % self.wsdl

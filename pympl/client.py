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
    def __init__(
            self, wsdl=None, guid=None, password=None, server_name=None,
            user_id=0, params=None):
        self._config_file = _load_config_file()
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

    #def table(self, name, primary_key=None):
    #    return Table(self, name, primary_key=primary_key)

    #def record(self, table_name, primary_key=None, **kwargs):
    #    return self.table(table_name, primary_key).record(**kwargs)

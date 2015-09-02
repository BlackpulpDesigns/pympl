from pympl.requeststring import RequestString


class StoredProcedure(object):
    def __init__(self, client, name):
        self.client = client
        self.name = name

    def __call__(self, **kwargs):
        return self.make_request(**kwargs).call()

    def make_request(self, *args, **kwargs):
        return self.client.fn.ExecuteStoredProcedure.make_request(
            StoredProcedureName=self.name,
            RequestString=str(RequestString(kwargs))
        )


class StoredProcedureFactory(object):
    def __init__(self, client):
        self.client = client

    def __getattr__(self, key):
        return StoredProcedure(self.client, key)
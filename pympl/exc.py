class PymplError(Exception):
    pass


class ServerError(PymplError):
    pass


class ResolverError(ServerError):
    pass


class FunctionError(ServerError):
    pass


class AddRecordError(FunctionError):
    pass


class UpdateRecordError(FunctionError):
    pass
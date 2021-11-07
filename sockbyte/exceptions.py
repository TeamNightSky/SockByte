class BaseError(Exception):
    pass


class SocketError(BaseError):
    pass


class ContentTypeError(BaseError):
    pass


class MalformedChunkError(BaseError):
    pass

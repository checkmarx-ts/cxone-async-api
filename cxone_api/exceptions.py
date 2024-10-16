import re

class EndpointException(BaseException):
    pass


class AuthException(BaseException):
    pass
    
class CommunicationException(BaseException):

    @staticmethod
    def __clean(content):
        if isinstance(content, list):
            return [CommunicationException.__clean(x) for x in content]
        elif isinstance(content, tuple):
            return (CommunicationException.__clean(x) for x in content)
        elif isinstance(content, dict):
            return {k:CommunicationException.__clean(v) for k,v in content.items()}
        elif isinstance(content, str):
            if re.match("^Bearer.*", content):
                return "REDACTED"
            else:
                return content
        else:
            return content

    def __init__(self, op, *args, **kwargs):
        BaseException.__init__(self, f"Operation: {op.__name__} args: "
            f"[{CommunicationException.__clean(args)}]"
            f" kwargs: [{CommunicationException.__clean(kwargs)}]")

class ResponseException(BaseException):
    pass

class ScanException(BaseException):
    pass

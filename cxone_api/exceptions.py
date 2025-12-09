import re
from typing import Type, Any, List

class EndpointException(BaseException):...

class AuthException(BaseException):...
    
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

class ResponseException(BaseException):...

class ScanException(BaseException):...

class ConfigurationException(BaseException):

    @staticmethod
    def wrong_type(value : Any, type : Type):
        return ConfigurationException(f"Value of [{value}] is not of type [{type}].")

    @staticmethod
    def not_in_enum(value : Any, valid_values : List[str]):
        return ConfigurationException(f"Value of [{value}] is not one of {valid_values}.")

    @staticmethod
    def read_only():
        return ConfigurationException("Configuration values are read-only.")

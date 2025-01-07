import urllib
from .exceptions import EndpointException
from .client import CxOneClient
import validators

DEFAULT_SCHEME = "https"

class CxOneAuthEndpoint:

    __AUTH_PREFIX = "/auth/realms"
    __AUTH_SUFFIX = "protocol/openid-connect/token"
    __ADMIN_PREFIX = "/auth/admin/realms"

    def __init__(self, tenant_name, server, scheme=DEFAULT_SCHEME):
        if tenant_name is None:
            raise EndpointException("Tenant name is required.")

        if server is None:
            raise EndpointException("Server name is required.")
        
        if scheme is None:
            raise EndpointException("Scheme is required.")
        
        self.__endpoint_url = urllib.parse.urlunsplit((scheme, server, 
            f"{CxOneAuthEndpoint.__AUTH_PREFIX}/{tenant_name}/{CxOneAuthEndpoint.__AUTH_SUFFIX}", 
            None, None))

        if not validators.url(self.__endpoint_url):
            raise EndpointException(f"{self.__endpoint_url} is not a valid URL.")

        self.__admin_endpoint_url = urllib.parse.urlunsplit((scheme, server, 
            f"{CxOneAuthEndpoint.__ADMIN_PREFIX}/{tenant_name}/", None, None))

        if not validators.url(self.__admin_endpoint_url):
            raise EndpointException(f"{self.__admin_endpoint_url} is not a valid URL.")

    @property
    def admin_endpoint(self):
        return self.__admin_endpoint_url

    def __str__(self):
        return str(self.__endpoint_url)


class AuthUS(CxOneAuthEndpoint):
    def __init__(self, tenant_name):
        super().__init__(tenant_name, "iam.checkmarx.net")

class AuthUS2(CxOneAuthEndpoint):
    def __init__(self, tenant_name):
        super().__init__(tenant_name, "us.iam.checkmarx.net")

class AuthEU(CxOneAuthEndpoint):
    def __init__(self, tenant_name):
        super().__init__(tenant_name, "eu.iam.checkmarx.net")

class AuthDEU(CxOneAuthEndpoint):
    def __init__(self, tenant_name):
        super().__init__(tenant_name, "deu.iam.checkmarx.net")

class AuthANZ(CxOneAuthEndpoint):
    def __init__(self, tenant_name):
        super().__init__(tenant_name, "anz.iam.checkmarx.net")

class AuthIndia(CxOneAuthEndpoint):
    def __init__(self, tenant_name):
        super().__init__(tenant_name, "ind.iam.checkmarx.net")

class AuthSingapore(CxOneAuthEndpoint):
    def __init__(self, tenant_name):
        super().__init__(tenant_name, "sng.iam.checkmarx.net")

class AuthUAE(CxOneAuthEndpoint):
    def __init__(self, tenant_name):
        super().__init__(tenant_name, "mea.iam.checkmarx.net")

AuthRegionEndpoints = {
    "US" : AuthUS,
    "US2" : AuthUS2,
    "EU" : AuthEU,
    "EU2" : AuthEU,
    "DEU" : AuthDEU,
    "ANZ" : AuthANZ,
    "India" : AuthIndia,
    "Singapore" : AuthSingapore,
    "UAE" : AuthUAE
}

class CxOneApiEndpoint:
    def __init__(self, server, scheme=DEFAULT_SCHEME):

        if server is None:
            raise EndpointException("Server name is required.")

        if scheme is None:
            raise EndpointException("Scheme name is required.")

        self.__endpoint_url = urllib.parse.urlunsplit((scheme, server, "/api/", None, None))

        if not validators.url(self.__endpoint_url):
            raise EndpointException(f"{self.__endpoint_url} is not a valid URL.")

        self.__root_url = urllib.parse.urlunsplit((scheme, server, "/", None, None))

        if not validators.url(self.__root_url):
            raise EndpointException(f"{self.__root_url} is not a valid URL.")

    def __str__(self):
        return str(self.__endpoint_url)

    @property
    def display_endpoint(self):
        return self.__root_url

class ApiUS(CxOneApiEndpoint):
    def __init__(self):
        super().__init__("ast.checkmarx.net")

class ApiUS2(CxOneApiEndpoint):
    def __init__(self):
        super().__init__("us.ast.checkmarx.net")

class ApiEU(CxOneApiEndpoint):
    def __init__(self):
        super().__init__("eu.ast.checkmarx.net")

class ApiEU2(CxOneApiEndpoint):
    def __init__(self):
        super().__init__("eu-2ast.checkmarx.net")

class ApiDEU(CxOneApiEndpoint):
    def __init__(self):
        super().__init__("deu.ast.checkmarx.net")

class ApiANZ(CxOneApiEndpoint):
    def __init__(self):
        super().__init__("anz.ast.checkmarx.net")

class ApiIndia(CxOneApiEndpoint):
    def __init__(self):
        super().__init__("ind.ast.checkmarx.net")

class ApiSingapore(CxOneApiEndpoint):
    def __init__(self):
        super().__init__("sng.ast.checkmarx.net")

class ApiUAE(CxOneApiEndpoint):
    def __init__(self):
        super().__init__("mea.ast.checkmarx.net")


ApiRegionEndpoints = {
    "US" : ApiUS,
    "US2" : ApiUS2,
    "EU" : ApiEU,
    "EU2" : ApiEU2,
    "DEU" : ApiDEU,
    "ANZ" : ApiANZ,
    "India" : ApiIndia,
    "Singapore" : ApiSingapore,
    "UAE" : ApiUAE
}

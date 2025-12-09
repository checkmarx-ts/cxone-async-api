import urllib
from .exceptions import EndpointException
from .client import CxOneClient
import validators

DEFAULT_SCHEME = "https"

class CxOneAuthEndpoint:
    """Defines an endpoint for Checkmarx One authorization.

    :param tenant_name: The name of the Checkmarx One tenant.
    :type tenant_name: str

    :param server: The FQDN of the Checkmarx One IAM server.
    :type server: str

    :param scheme: The HTTP protocol scheme for communicating with the IAM server.  Defaults to "https"
    :type scheme: str, optional

    """

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
        """The URL for the IAM administrative endpoint."""
        return self.__admin_endpoint_url

    def __str__(self):
        return str(self.__endpoint_url)


class AuthUS(CxOneAuthEndpoint):
    """Defines an well-known multi-tenant endpoint for Checkmarx One authorization.

    :param tenant_name: The name of the Checkmarx One tenant.
    :type tenant_name: str
    """
    def __init__(self, tenant_name):
        super().__init__(tenant_name, "iam.checkmarx.net")

class AuthUS2(CxOneAuthEndpoint):
    """Defines an well-known multi-tenant endpoint for Checkmarx One authorization.

    :param tenant_name: The name of the Checkmarx One tenant.
    :type tenant_name: str
    """
    def __init__(self, tenant_name):
        super().__init__(tenant_name, "us.iam.checkmarx.net")

class AuthEU(CxOneAuthEndpoint):
    """Defines an well-known multi-tenant endpoint for Checkmarx One authorization.

    :param tenant_name: The name of the Checkmarx One tenant.
    :type tenant_name: str
    """
    def __init__(self, tenant_name):
        super().__init__(tenant_name, "eu.iam.checkmarx.net")

class AuthEU2(CxOneAuthEndpoint):
    """Defines an well-known multi-tenant endpoint for Checkmarx One authorization.

    :param tenant_name: The name of the Checkmarx One tenant.
    :type tenant_name: str
    """
    def __init__(self, tenant_name):
        super().__init__(tenant_name, "eu-2.iam.checkmarx.net")

class AuthDEU(CxOneAuthEndpoint):
    """Defines an well-known multi-tenant endpoint for Checkmarx One authorization.

    :param tenant_name: The name of the Checkmarx One tenant.
    :type tenant_name: str
    """
    def __init__(self, tenant_name):
        super().__init__(tenant_name, "deu.iam.checkmarx.net")

class AuthANZ(CxOneAuthEndpoint):
    """Defines an well-known multi-tenant endpoint for Checkmarx One authorization.

    :param tenant_name: The name of the Checkmarx One tenant.
    :type tenant_name: str
    """
    def __init__(self, tenant_name):
        super().__init__(tenant_name, "anz.iam.checkmarx.net")

class AuthIndia(CxOneAuthEndpoint):
    """Defines an well-known multi-tenant endpoint for Checkmarx One authorization.

    :param tenant_name: The name of the Checkmarx One tenant.
    :type tenant_name: str
    """
    def __init__(self, tenant_name):
        super().__init__(tenant_name, "ind.iam.checkmarx.net")

class AuthSingapore(CxOneAuthEndpoint):
    """Defines an well-known multi-tenant endpoint for Checkmarx One authorization.

    :param tenant_name: The name of the Checkmarx One tenant.
    :type tenant_name: str
    """
    def __init__(self, tenant_name):
        super().__init__(tenant_name, "sng.iam.checkmarx.net")

class AuthUAE(CxOneAuthEndpoint):
    """Defines an well-known multi-tenant endpoint for Checkmarx One authorization.

    :param tenant_name: The name of the Checkmarx One tenant.
    :type tenant_name: str
    """
    def __init__(self, tenant_name):
        super().__init__(tenant_name, "mea.iam.checkmarx.net")



AuthRegionEndpoints = { 
    "US" : AuthUS,
    "US2" : AuthUS2,
    "EU" : AuthEU,
    "EU2" : AuthEU2,
    "DEU" : AuthDEU,
    "ANZ" : AuthANZ,
    "India" : AuthIndia,
    "Singapore" : AuthSingapore,
    "UAE" : AuthUAE
}
"""A map of string monikers representing well-known multi-tenant Checkmarx One endpoints to the proper endpoint implementation.

Example:

>>> AuthRegionEndpoints['US']("mytenantname")
""" 

class CxOneApiEndpoint:
    """Defines an endpoint for Checkmarx One API access.

    :param server: The FQDN of the Checkmarx One API server.
    :type server: str

    :param scheme: The HTTP protocol scheme for communicating with the API server.  Defaults to "https"
    :type scheme: str, optional

    """

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
        """The URL for use when building links to UI views."""
        return self.__root_url

class ApiUS(CxOneApiEndpoint):
    """Defines an endpoint for well-known multi-tenant Checkmarx One API access."""
    def __init__(self):
        super().__init__("ast.checkmarx.net")

class ApiUS2(CxOneApiEndpoint):
    """Defines an endpoint for well-known multi-tenant Checkmarx One API access."""
    def __init__(self):
        super().__init__("us.ast.checkmarx.net")

class ApiEU(CxOneApiEndpoint):
    """Defines an endpoint for well-known multi-tenant Checkmarx One API access."""
    def __init__(self):
        super().__init__("eu.ast.checkmarx.net")

class ApiEU2(CxOneApiEndpoint):
    """Defines an endpoint for well-known multi-tenant Checkmarx One API access."""
    def __init__(self):
        super().__init__("eu-2.ast.checkmarx.net")

class ApiDEU(CxOneApiEndpoint):
    """Defines an endpoint for well-known multi-tenant Checkmarx One API access."""
    def __init__(self):
        super().__init__("deu.ast.checkmarx.net")

class ApiANZ(CxOneApiEndpoint):
    """Defines an endpoint for well-known multi-tenant Checkmarx One API access."""
    def __init__(self):
        super().__init__("anz.ast.checkmarx.net")

class ApiIndia(CxOneApiEndpoint):
    """Defines an endpoint for well-known multi-tenant Checkmarx One API access."""
    def __init__(self):
        super().__init__("ind.ast.checkmarx.net")

class ApiSingapore(CxOneApiEndpoint):
    """Defines an endpoint for well-known multi-tenant Checkmarx One API access."""
    def __init__(self):
        super().__init__("sng.ast.checkmarx.net")

class ApiUAE(CxOneApiEndpoint):
    """Defines an endpoint for well-known multi-tenant Checkmarx One API access."""
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
"""A map of string monikers representing well-known multi-tenant Checkmarx One endpoints to the proper endpoint implementation.

Example:

>>> ApiRegionEndpoints['US']()
""" 

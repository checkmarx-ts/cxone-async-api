import requests
from requests.compat import urljoin
from ..util import join_query_dict
from ..client import CxOneClient
from deprecation import deprecated
from ..__version__ import __version__

@deprecated("1.0.3", current_version=__version__, details="Use access_mgmt.user_mgmt.retrieve_groups")
async def retrieve_groups(client : CxOneClient, **kwargs) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = join_query_dict(urljoin(client.admin_endpoint, "groups"), kwargs)
    return await client.exec_request(requests.get, url)

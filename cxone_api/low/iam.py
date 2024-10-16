import requests
from requests.compat import urljoin
from ..util import join_query_dict
from ..client import CxOneClient

async def retrieve_groups(client : CxOneClient, **kwargs) -> requests.Response:
    url = join_query_dict(urljoin(client.admin_endpoint, "groups"), kwargs)
    return await client.exec_request(requests.get, url)

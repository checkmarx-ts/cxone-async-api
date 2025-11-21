from ...client import CxOneClient
from ...util import join_query_dict
import requests
from requests.compat import urljoin

async def retrieve_groups(client : CxOneClient, **kwargs) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = join_query_dict(urljoin(client.api_endpoint, "access-management/groups"), kwargs)
    return await client.exec_request(requests.get, url)

async def retrieve_users(client : CxOneClient, **kwargs) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = join_query_dict(urljoin(client.api_endpoint, "access-management/users"), kwargs)
    return await client.exec_request(requests.get, url)

async def retrieve_clients(client : CxOneClient) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = urljoin(client.api_endpoint, "access-management/clients")
    return await client.exec_request(requests.get, url)

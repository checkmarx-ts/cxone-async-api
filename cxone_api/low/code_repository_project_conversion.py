import requests
from typing import List, Dict
from requests.compat import urljoin
from ..client import CxOneClient
from ..util import join_query_dict


async def convert_a_project(client : CxOneClient, body : Dict) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = urljoin(client.api_endpoint, "repos-manager/project-conversion")
    return await client.exec_request(requests.post, url, json=body)


async def retrieve_conversion_status(client : CxOneClient, processId : str) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = urljoin(client.api_endpoint, "repos-manager/project-conversion")
    url = join_query_dict(url, {"processId" : processId})
    return await client.exec_request(requests.get, url)

import requests
from typing import Dict
from requests.compat import urljoin
from ..util import join_query_dict
from ..client import CxOneClient


async def retrieve_repo_by_id(client: CxOneClient, repoid: str) -> requests.Response:
    """|LowLevelApiDocstring| Endpoint: /api/repos-manager/repo/{repoid}"""
    url = urljoin(client.api_endpoint, f"repos-manager/repo/{repoid}")
    return await client.exec_request(requests.get, url)


async def update_repo_by_id_for_project(
    client: CxOneClient, repoid: str, projectid: str, payload: Dict
) -> requests.Response:
    """|LowLevelApiDocstring| Endpoint: /api/repos-manager/repo/{repoid}"""
    url = urljoin(client.api_endpoint, f"repos-manager/repo/{repoid}")
    url = join_query_dict(url, {"projectId": projectid})
    return await client.exec_request(requests.put, url, json=payload)


async def get_scm_by_id(client: CxOneClient, scmId: str) -> requests.Response:
    """|LowLevelApiDocstring| Endpoint: /api/repos-manager/getscmdtobyid"""
    url = urljoin(client.api_endpoint, f"repos-manager/getscmdtobyid?scmId={scmId}")
    return await client.exec_request(requests.get, url)

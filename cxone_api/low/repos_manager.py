import requests
from requests.compat import urljoin
from ..client import CxOneClient

async def retrieve_repo_by_id(client : CxOneClient, repoid : str) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = urljoin(client.api_endpoint, f"repos-manager/repo/{repoid}")
    return await client.exec_request(requests.get, url)


async def get_scm_by_id(client : CxOneClient, scmId : str) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = urljoin(client.api_endpoint, f"repos-manager/getscmdtobyid?scmId={scmId}")
    return await client.exec_request(requests.get, url)

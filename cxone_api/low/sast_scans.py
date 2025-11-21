import requests
from requests.compat import urljoin
from ..client import CxOneClient


# Undocumented APIs:

async def retrieve_scan_log(client : CxOneClient, scanid : str, stream=False) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = urljoin(client.api_endpoint, f"logs/{scanid}/sast")
    response = await client.exec_request(requests.get, url)

    if response.ok and response.status_code == 307:
        response = await client.exec_request(requests.get,
                                             response.headers['Location'], stream=stream)

    return response

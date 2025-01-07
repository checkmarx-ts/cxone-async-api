import requests
from ..client import CxOneClient
from requests.compat import urljoin

async def retrieve_preset_list(client : CxOneClient) -> requests.Response:
    url = urljoin(client.api_endpoint, "queries/presets")
    return await client.exec_request(requests.get, url)

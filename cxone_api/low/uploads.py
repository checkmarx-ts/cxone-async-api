import requests
from requests.compat import urljoin
from ..client import CxOneClient


async def generate_upload_link(client : CxOneClient) -> requests.Response:
    url = urljoin(client.api_endpoint, "uploads")
    return await client.exec_request(requests.post, url)

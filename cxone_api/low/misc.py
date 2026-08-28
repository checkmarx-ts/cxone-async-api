import requests
from ..client import CxOneClient
from requests.compat import urljoin


async def retrieve_preset_list(client: CxOneClient) -> requests.Response:
    """|LowLevelApiDocstring| Endpoint: /api/queries/presets"""
    url = urljoin(client.api_endpoint, "queries/presets")
    return await client.exec_request(requests.get, url)


async def retrieve_versions(client: CxOneClient) -> requests.Response:
    """|LowLevelApiDocstring| Endpoint: /api/versions"""
    url = urljoin(client.api_endpoint, "versions")
    return await client.exec_request(requests.get, url)


async def retrieve_feature_flags(client: CxOneClient) -> requests.Response:
    """|LowLevelApiDocstring| Endpoint: /api/flags"""
    url = urljoin(client.api_endpoint, "flags")
    return await client.exec_request(requests.get, url)

import requests
from cxone_api import CxOneClient
from cxone_api.util import join_query_dict
from requests.compat import urljoin


async def create_a_report(client: CxOneClient, **kwargs) -> requests.Response:
    """|LowLevelApiDocstring| Verb: POST Endpoint: /api/sca/export/requests"""
    url = urljoin(client.api_endpoint, "sca/export/requests")
    return await client.exec_request(requests.post, url, json=kwargs)

async def retrieve_report_status(
    client: CxOneClient, exportId: str
) -> requests.Response:
    """|LowLevelApiDocstring| Verb: GET Endpoint: /api/sca/export/requests"""
    url = urljoin(client.api_endpoint, "sca/export/requests")
    url = join_query_dict(url, {"exportId": exportId})
    return await client.exec_request(requests.get, url)

async def retrieve_list_of_report_formats(client: CxOneClient) -> requests.Response:
    """|LowLevelApiDocstring| Verb: GET Endpoint: /api/sca/export/file-formats"""
    url = urljoin(client.api_endpoint, "sca/export/file-formats")
    return await client.exec_request(requests.get, url)

async def download_a_report(client: CxOneClient, exportId: str) -> requests.Response:
    """|LowLevelApiDocstring| Verb: GET Endpoint: /api/sca/export/requests/{exportId}/download"""
    url = urljoin(client.api_endpoint, f"sca/export/requests/{exportId}/download")
    return await client.exec_request(requests.get, url)

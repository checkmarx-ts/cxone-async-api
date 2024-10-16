import requests
from requests.compat import urljoin
from ..client import CxOneClient
from ..util import join_query_dict

async def create_a_report(client : CxOneClient, **kwargs) -> requests.Response:
    url = urljoin(client.api_endpoint, f"reports")
    return await client.exec_request(requests.post, url, json=kwargs)

async def retrieve_report_status(client : CxOneClient, reportid : str, **kwargs) -> requests.Response:
    url = urljoin(client.api_endpoint, f"reports/{reportid}")
    url = join_query_dict(url, kwargs)
    return await client.exec_request(requests.get, url)

async def download_a_report(client : CxOneClient, reportid : str) -> requests.Response:
    url = urljoin(client.api_endpoint, f"reports/{reportid}/download")
    return await client.exec_request(requests.get, url)

import requests
from requests.compat import urljoin
from ..client import CxOneClient
from ..util import dashargs, join_query_dict


@dashargs("scan-ids")
async def retrieve_scans_metadata(client : CxOneClient, **kwargs) -> requests.Response:
    url = urljoin(client.api_endpoint, "sast-metadata")
    url = join_query_dict(url, kwargs)
    return await client.exec_request(requests.get, url)

async def retrieve_scan_metadata(client : CxOneClient, scanid) -> requests.Response:
    url = urljoin(client.api_endpoint, f"sast-metadata/{scanid}")
    return await client.exec_request(requests.get, url)

async def retrieve_scan_metrics(client : CxOneClient, scanid) -> requests.Response:
    url = urljoin(client.api_endpoint, f"sast-metadata/{scanid}/metrics")
    return await client.exec_request(requests.get, url)

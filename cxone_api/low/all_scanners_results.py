import requests
from cxone_api import CxOneClient
from cxone_api.util import join_query_dict, dashargs
from requests.compat import urljoin

@dashargs("scan-id", "exclude-result-types")
async def retrieve_scan_results_all_scanners(client : CxOneClient, **kwargs) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = urljoin(client.api_endpoint, "results")
    url = join_query_dict(url, kwargs)
    return await client.exec_request(requests.get, url)

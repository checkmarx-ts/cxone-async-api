import requests
from cxone_api import CxOneClient
from cxone_api.util import join_query_dict, dashargs
from requests.compat import urljoin


async def retrieve_apisec_security_risks(client : CxOneClient, scan_id : str, **kwargs) -> requests.Response:
    url = urljoin(client.api_endpoint, f"apisec/static/api/risks/{scan_id}")
    url = join_query_dict(url, kwargs)
    return await client.exec_request(requests.get, url)

async def retrieve_risk_details(client : CxOneClient, risk_id : str) -> requests.Response:
    url = urljoin(client.api_endpoint, f"apisec/static/api/risks//risk/{risk_id}")
    return await client.exec_request(requests.get, url)

import requests
from typing import Iterable
from cxone_api import CxOneClient
from requests.compat import urljoin

async def get_sast_query_description(client : CxOneClient, ids : Iterable[int]) -> requests.Response:
    url = urljoin(client.api_endpoint, "queries/descriptions")
    query_args = "&".join([f"ids={x}" for x in set(ids)])
    url = url + f"?{query_args}"
    return await client.exec_request(requests.get, url)
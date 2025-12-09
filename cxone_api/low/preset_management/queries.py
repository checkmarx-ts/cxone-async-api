import requests
from requests.compat import urljoin
from cxone_api.util import dashargs, join_query_dict
from cxone_api.client import CxOneClient

@dashargs("search-term")
async def retrieve_list_of_query_families (client : CxOneClient, scanner : str, **kwargs) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = urljoin(client.api_endpoint, f"preset-manager/{scanner}/query-families")
    url = join_query_dict(url, kwargs)    
    return await client.exec_request(requests.get, url)

@dashargs("search-term")
async def retrieve_list_of_queries_in_a_family (client : CxOneClient, scanner : str, family : str, **kwargs) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = urljoin(client.api_endpoint, f"preset-manager/{scanner}/query-families/{family}/queries")
    url = join_query_dict(url, kwargs)    
    return await client.exec_request(requests.get, url)

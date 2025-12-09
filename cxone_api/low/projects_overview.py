import requests
from requests.compat import urljoin
from ..util import dashargs, join_query_dict
from ..client import CxOneClient

@dashargs("from-date", "group-ids", "risk-level", "scan-origin", "source-type", "tag-keys", "tag-values", "to-date")
async def retrieve_projects_overview(client : CxOneClient, **kwargs) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = urljoin(client.api_endpoint, "projects-overview")
    url = join_query_dict(url, kwargs)    
    return await client.exec_request(requests.get, url)

@dashargs("from-date", "group-ids", "risk-level", "scan-origin", "source-type", "tag-keys", "tag-values", "to-date", "group-by-field")
async def retrieve_aggregated_results(client : CxOneClient, **kwargs) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = urljoin(client.api_endpoint, "projects-overview/aggregate")
    url = join_query_dict(url, kwargs)    
    return await client.exec_request(requests.get, url)

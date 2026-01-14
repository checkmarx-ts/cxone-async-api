import requests
from requests.compat import urljoin
from cxone_api.util import join_query_dict
from cxone_api import CxOneClient

async def retrieve_policy_violation_info(client : CxOneClient, astProjectId : str, scanId : str) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = urljoin(client.api_endpoint, "policy_management_service_uri/evaluation")
    url = join_query_dict(url, { "astProjectId" : astProjectId, "scanId" : scanId})    
    return await client.exec_request(requests.get, url)


async def retrieve_all_policies(client : CxOneClient, page : int, limit : int = 20, policyName : str = None) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = urljoin(client.api_endpoint, "policy_management_service_uri/policies/v2")

    query = {
        "limit" : limit,
        "page" : page
    }

    if policyName is not None:
        query['policyName'] = policyName

    url = join_query_dict(url, query)    
    return await client.exec_request(requests.get, url)

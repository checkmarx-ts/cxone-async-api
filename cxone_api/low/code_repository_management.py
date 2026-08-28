import requests
from typing import List, Dict
from requests.compat import urljoin
from ..client import CxOneClient
from ..util import join_query_dict


async def retrieve_list_of_scms(client: CxOneClient, **kwargs) -> requests.Response:
    """|LowLevelApiDocstring| Endpoint: /api/repos-manager/v2/scms"""
    url = urljoin(client.api_endpoint, "repos-manager/v2/scms")
    url = join_query_dict(url, kwargs)
    return await client.exec_request(requests.get, url)


async def retrieve_scm_projects(
    client: CxOneClient, scmid: str, limit: int, offset: int
) -> requests.Response:
    """|LowLevelApiDocstring| Endpoint: /api/repos-manager/scms/{scmid}/projects"""
    url = urljoin(client.api_endpoint, f"repos-manager/scms/{scmid}/projects")
    url = join_query_dict(url, {"limit": limit, "offset": offset})
    return await client.exec_request(requests.get, url)


async def disconnect_project_from_scm(
    client: CxOneClient, projectid: str
) -> requests.Response:
    """|LowLevelApiDocstring| Endpoint: /api/repos-manager/projects/{projectid}/disconnect"""
    url = urljoin(client.api_endpoint, f"repos-manager/projects/{projectid}/disconnect")
    return await client.exec_request(requests.post, url)


async def retrieve_protected_branches(
    client: CxOneClient, project_name: str
) -> requests.Response:
    """|LowLevelApiDocstring| Endpoint: /api/repos-manager/protected-branches"""
    url = urljoin(client.api_endpoint, "repos-manager/protected-branches")
    url = join_query_dict(url, {"cxProjectName": project_name})
    return await client.exec_request(requests.get, url)


async def add_protected_branches(
    client: CxOneClient, project_name: str, branch_details: List[Dict]
) -> requests.Response:
    """|LowLevelApiDocstring| Endpoint: /api/repos-manager/protected-branches"""
    url = urljoin(client.api_endpoint, "repos-manager/protected-branches")
    url = join_query_dict(url, {"cxProjectName": project_name})
    return await client.exec_request(requests.post, url, json=branch_details)


async def replace_protected_branches(
    client: CxOneClient, project_name: str, branch_details: List[Dict]
) -> requests.Response:
    """|LowLevelApiDocstring| Endpoint: /api/repos-manager/protected-branches"""
    url = urljoin(client.api_endpoint, "repos-manager/protected-branches")
    url = join_query_dict(url, {"cxProjectName": project_name})
    return await client.exec_request(requests.put, url, json=branch_details)

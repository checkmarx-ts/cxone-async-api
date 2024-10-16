import requests
from requests.compat import urljoin
from ..util import dashargs, join_query_dict
from ..client import CxOneClient

async def create_a_project(client : CxOneClient, **kwargs) -> requests.Response:
    url = urljoin(client.api_endpoint, "projects")
    return await client.exec_request(requests.post, url, json=kwargs)

@dashargs("repo-url", "name-regex", "tags-keys", "tags-values")
async def retrieve_list_of_projects(client : CxOneClient, **kwargs) -> requests.Response:
    url = urljoin(client.api_endpoint, "projects")
    url = join_query_dict(url, kwargs)
    return await client.exec_request(requests.get, url)

async def retrieve_list_of_tags(client : CxOneClient) -> requests.Response:
    url = urljoin(client.api_endpoint, "projects/tags")
    return await client.exec_request(requests.get, url)

@dashargs("application-id", "project-ids", "scan-status")
async def retrieve_last_scan(client : CxOneClient, **kwargs) -> requests.Response:
    url = urljoin(client.api_endpoint, "projects/last-scan")
    url = join_query_dict(url, kwargs)
    return await client.exec_request(requests.get, url)

@dashargs("branch-name", "project-id")
async def retrieve_list_of_branches(client : CxOneClient) -> requests.Response:
    url = urljoin(client.api_endpoint, "projects/branches")
    return await client.exec_request(requests.get, url)

async def retrieve_project_info(client : CxOneClient, projectid : str) -> requests.Response:
    url = urljoin(client.api_endpoint, f"projects/{projectid}")
    return await client.exec_request(requests.get, url)

async def update_a_project(client : CxOneClient, projectid : str, payload : dict) -> requests.Response:
    url = urljoin(client.api_endpoint, f"projects/{projectid}")
    return await client.exec_request(requests.put, url, json=payload)

async def delete_a_project(client : CxOneClient, projectid : str) -> requests.Response:
    url = urljoin(client.api_endpoint, f"projects/{projectid}")
    return await client.exec_request(requests.delete, url)


# Undocumented APIs:

async def retrieve_project_configuration(client : CxOneClient, projectid : str) -> requests.Response:
    url = urljoin(client.api_endpoint, f"configuration/project?project-id={projectid}")
    return await client.exec_request(requests.get, url)

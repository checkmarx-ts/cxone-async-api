import requests
from typing import List
from requests.compat import urljoin
from ..util import dashargs, join_query_dict
from ..client import CxOneClient

async def retrieve_tenant_configuration(client : CxOneClient) -> requests.Response:
    url = urljoin(client.api_endpoint, "configuration/tenant")
    return await client.exec_request(requests.get, url)

async def update_tenant_configuration(client : CxOneClient, configs : List[dict]) -> requests.Response:
    url = urljoin(client.api_endpoint, "configuration/tenant")
    return await client.exec_request(requests.patch, url, json=configs)

@dashargs("config-keys")
async def delete_tenant_configuration(client : CxOneClient, **kwargs) -> requests.Response:
    url = urljoin(client.api_endpoint, "configuration/tenant")
    url = join_query_dict(url, kwargs)
    return await client.exec_request(requests.delete, url)

@dashargs("project-id")
async def retrieve_project_configuration(client : CxOneClient, **kwargs) -> requests.Response:
    url = urljoin(client.api_endpoint, "configuration/project")
    url = join_query_dict(url, kwargs)
    return await client.exec_request(requests.get, url)

@dashargs("project-id")
async def update_project_configuration(client : CxOneClient, configs : List[dict], **kwargs) -> requests.Response:
    url = urljoin(client.api_endpoint, "configuration/project")
    url = join_query_dict(url, kwargs)
    return await client.exec_request(requests.patch, url, json=configs)

@dashargs("config-keys", "project-id")
async def delete_project_configuration(client : CxOneClient, **kwargs) -> requests.Response:
    url = urljoin(client.api_endpoint, "configuration/project")
    url = join_query_dict(url, kwargs)
    return await client.exec_request(requests.delete, url)

@dashargs("scan-id")
async def retrieve_scan_configuration(client : CxOneClient, **kwargs) -> requests.Response:
    url = urljoin(client.api_endpoint, "configuration/scan")
    url = join_query_dict(url, kwargs)
    return await client.exec_request(requests.get, url)

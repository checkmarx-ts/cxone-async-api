import requests
from requests.compat import urljoin
from ..client import CxOneClient
from ..util import dashargs, join_query_dict

async def run_a_scan(client : CxOneClient, payload : dict) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = urljoin(client.api_endpoint, "scans")
    return await client.exec_request(requests.post, url, json=payload)

@dashargs("from-date", "project-id", "project-ids", "scan-ids", "project-names", "source-origin", "source-type", "tags-keys", "tags-values", "to-date")
async def retrieve_list_of_scans(client : CxOneClient, **kwargs) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = urljoin(client.api_endpoint, "scans")
    url = join_query_dict(url, kwargs)
    return await client.exec_request(requests.get, url)

async def retrieve_scan_details(client : CxOneClient, scanid : str) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = urljoin(client.api_endpoint, f"scans/{scanid}")
    return await client.exec_request(requests.get, url)

async def cancel_a_scan(client : CxOneClient, scanid : str) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = urljoin(client.api_endpoint, f"scans/{scanid}")
    return await client.exec_request(requests.patch, url)

async def delete_a_scan(client : CxOneClient, scanid : str) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = urljoin(client.api_endpoint, f"scans/{scanid}")
    return await client.exec_request(requests.delete, url)

async def retrieve_scan_workflow(client : CxOneClient, scanid : str, **kwargs):
    """|LowLevelApiDocstring|"""
    url = urljoin(client.api_endpoint, f"scans/{scanid}/workflow")
    url = join_query_dict(url, kwargs)
    return await client.exec_request(requests.get, url)

async def retrieve_scan_status_summary(client : CxOneClient) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = urljoin(client.api_endpoint, "scans/summary")
    return await client.exec_request(requests.get, url)

async def retrieve_templates(client : CxOneClient) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = urljoin(client.api_endpoint, "scans/templates")
    return await client.exec_request(requests.get, url)

async def retrieve_template_file(client : CxOneClient, filename : str) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = urljoin(client.api_endpoint, f"scans/templates/{filename}")
    return await client.exec_request(requests.get, url)

async def retrieve_tags(client : CxOneClient) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = urljoin(client.api_endpoint, "scans/tags")
    return await client.exec_request(requests.get, url)

async def update_scan_tags(client : CxOneClient, scan_id : str, payload : dict) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = urljoin(client.api_endpoint, f"scans/{scan_id}/tags")
    return await client.exec_request(requests.put, url, json=payload)

async def retrieve_values_for_fields(client : CxOneClient, **kwargs) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = urljoin(client.api_endpoint, "scans/fieldValues")
    url = join_query_dict(url, kwargs)
    return await client.exec_request(requests.get, url)

# Undocumented APIs:

async def run_a_repo_scan(client : CxOneClient, scmid : str, projectId : str, repo_org : str, payload : dict) -> requests.Response:
    """|LowLevelApiDocstring|"""
    url = urljoin(client.api_endpoint, f"repos-manager/scms/{scmid}/orgs/{repo_org}/repo/projectScan?projectId={projectId}")
    return await client.exec_request(requests.post, url, json=payload)

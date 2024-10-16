import requests
from requests.compat import urljoin
from ..util import dashargs, join_query_dict
from ..client import CxOneClient


async def create_an_application(client : CxOneClient, **kwargs) -> requests.Response:
    url = urljoin(client.api_endpoint, "applications")
    return await client.exec_request(requests.post, url, json=kwargs)

@dashargs("tags-keys", "tags-values")
async def retrieve_applications_info(client : CxOneClient, **kwargs) -> requests.Response:
    url = urljoin(client.api_endpoint, "applications")
    url = join_query_dict(url, kwargs)
    return await client.exec_request(requests.get, url)

async def retrieve_list_of_tags(client : CxOneClient) -> requests.Response:
    url = urljoin(client.api_endpoint, "applications/tags")
    return await client.exec_request(requests.get, url)

async def retrieve_an_application(client : CxOneClient, app_id : str) -> requests.Response:
    url = urljoin(client.api_endpoint, f"applications/{app_id}")
    return await client.exec_request(requests.get, url)

async def update_an_application(client : CxOneClient, app_id : str, **kwargs) -> requests.Response:
    url = urljoin(client.api_endpoint, f"applications/{app_id}")
    return await client.exec_request(requests.put, url, json=kwargs)

async def delete_an_application(client : CxOneClient, app_id : str) -> requests.Response:
    url = urljoin(client.api_endpoint, f"applications/{app_id}")
    return await client.exec_request(requests.delete, url)

async def create_an_application_rule(client : CxOneClient, app_id : str, **kwargs) -> requests.Response:
    url = urljoin(client.api_endpoint, f"applications/{app_id}/project-rules")
    return await client.exec_request(requests.post, url, json=kwargs)

async def retrieve_list_of_application_rules (client : CxOneClient, app_id : str) -> requests.Response:
    url = urljoin(client.api_endpoint, f"applications/{app_id}/project-rules")
    return await client.exec_request(requests.get, url)

async def retrieve_an_application_rule (client : CxOneClient, app_id : str, rule_id : str) -> requests.Response:
    url = urljoin(client.api_endpoint, f"applications/{app_id}/project-rules/{rule_id}")
    return await client.exec_request(requests.get, url)

async def update_an_application_rule (client : CxOneClient, app_id : str, rule_id : str, **kwargs) -> requests.Response:
    url = urljoin(client.api_endpoint, f"applications/{app_id}/project-rules/{rule_id}")
    return await client.exec_request(requests.put, url, json=kwargs)

async def delete_an_application_rule (client : CxOneClient, app_id : str, rule_id : str) -> requests.Response:
    url = urljoin(client.api_endpoint, f"applications/{app_id}/project-rules/{rule_id}")
    return await client.exec_request(requests.delete, url)

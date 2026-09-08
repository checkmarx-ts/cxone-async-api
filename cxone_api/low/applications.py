import requests
from requests.compat import urljoin
from ..util import dashargs, join_query_dict
from ..client import CxOneClient


async def create_an_application(client: CxOneClient, **kwargs) -> requests.Response:
    """|LowLevelApiDocstring| Verb: POST Endpoint: /api/applications"""
    url = urljoin(client.api_endpoint, "applications")
    return await client.exec_request(requests.post, url, json=kwargs)


@dashargs("tags-keys", "tags-values")
async def retrieve_applications_info(
    client: CxOneClient, **kwargs
) -> requests.Response:
    """|LowLevelApiDocstring| Verb: GET Endpoint: /api/applications"""
    url = urljoin(client.api_endpoint, "applications")
    url = join_query_dict(url, kwargs)
    return await client.exec_request(requests.get, url)


async def retrieve_list_of_tags(client: CxOneClient) -> requests.Response:
    """|LowLevelApiDocstring| Verb: GET Endpoint: /api/applications/tags"""
    url = urljoin(client.api_endpoint, "applications/tags")
    return await client.exec_request(requests.get, url)


async def retrieve_an_application(
    client: CxOneClient, app_id: str
) -> requests.Response:
    """|LowLevelApiDocstring| Verb: GET Endpoint: /api/applications/{app_id}"""
    url = urljoin(client.api_endpoint, f"applications/{app_id}")
    return await client.exec_request(requests.get, url)

async def update_an_application(
    client: CxOneClient, app_id: str, **kwargs
) -> requests.Response:
    """|LowLevelApiDocstring| Verb: PUT Endpoint: /api/applications/{app_id}"""
    url = urljoin(client.api_endpoint, f"applications/{app_id}")
    return await client.exec_request(requests.put, url, json=kwargs)

async def update_specific_application_fields(
    client: CxOneClient, app_id: str, **kwargs
) -> requests.Response:
    """|LowLevelApiDocstring| Verb: PATCH Endpoint: /api/applications/{app_id}"""
    url = urljoin(client.api_endpoint, f"applications/{app_id}")
    return await client.exec_request(requests.patch, url, json=kwargs)

async def delete_an_application(client: CxOneClient, app_id: str) -> requests.Response:
    """|LowLevelApiDocstring| Verb: DELETE Endpoint: /api/applications/{app_id}"""
    url = urljoin(client.api_endpoint, f"applications/{app_id}")
    return await client.exec_request(requests.delete, url)


async def create_an_application_rule(
    client: CxOneClient, app_id: str, **kwargs
) -> requests.Response:
    """|LowLevelApiDocstring| Verb: POST Endpoint: /api/applications/{app_id}/project-rules"""
    url = urljoin(client.api_endpoint, f"applications/{app_id}/project-rules")
    return await client.exec_request(requests.post, url, json=kwargs)


async def retrieve_list_of_application_rules(
    client: CxOneClient, app_id: str
) -> requests.Response:
    """|LowLevelApiDocstring| Verb: GET Endpoint: /api/applications/{app_id}/project-rules"""
    url = urljoin(client.api_endpoint, f"applications/{app_id}/project-rules")
    return await client.exec_request(requests.get, url)


async def retrieve_an_application_rule(
    client: CxOneClient, app_id: str, rule_id: str
) -> requests.Response:
    """|LowLevelApiDocstring| Verb: GET Endpoint: /api/applications/{app_id}/project-rules/{rule_id}"""
    url = urljoin(client.api_endpoint, f"applications/{app_id}/project-rules/{rule_id}")
    return await client.exec_request(requests.get, url)


async def update_an_application_rule(
    client: CxOneClient, app_id: str, rule_id: str, **kwargs
) -> requests.Response:
    """|LowLevelApiDocstring| Verb: PUT Endpoint: /api/applications/{app_id}/project-rules/{rule_id}"""
    url = urljoin(client.api_endpoint, f"applications/{app_id}/project-rules/{rule_id}")
    return await client.exec_request(requests.put, url, json=kwargs)


async def delete_an_application_rule(
    client: CxOneClient, app_id: str, rule_id: str
) -> requests.Response:
    """|LowLevelApiDocstring| Verb: DELETE Endpoint: /api/applications/{app_id}/project-rules/{rule_id}"""
    url = urljoin(client.api_endpoint, f"applications/{app_id}/project-rules/{rule_id}")
    return await client.exec_request(requests.delete, url)

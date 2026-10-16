import requests
from cxone_api import CxOneClient
from cxone_api.util import join_query_dict
from requests.compat import urljoin
from typing import List


async def retrieve_configurations_by_project(
    client: CxOneClient, **kwargs
) -> requests.Response:
    """|LowLevelApiDocstring|

    Verb: GET
    Endpoint: /api/sca/registries-configuration/projects
    """
    url = urljoin(client.api_endpoint, "sca/registries-configuration/projects")
    url = join_query_dict(url, **kwargs)

    return await client.exec_request(requests.get, url)


async def retrieve_projects_associated_with_configuration(
    client: CxOneClient, configId: str
) -> requests.Response:
    """|LowLevelApiDocstring|

    Verb: GET
    Endpoint: /api/sca/registries-configuration/projects/configuration/{configId}
    """
    url = urljoin(
        client.api_endpoint,
        f"sca/registries-configuration/projects/configuration/{configId}",
    )

    return await client.exec_request(requests.get, url)


async def disassociate_all_projects_from_configuration(
    client: CxOneClient, configId: str
) -> requests.Response:
    """|LowLevelApiDocstring|

    Verb: DELETE
    Endpoint: /api/sca/registries-configuration/projects/configuration/{configId}
    """
    url = urljoin(
        client.api_endpoint,
        f"sca/registries-configuration/projects/configuration/{configId}",
    )

    return await client.exec_request(requests.delete, url)


async def associate_projects_with_configuration(
    client: CxOneClient, configId: str, projectIds: List[str]
) -> requests.Response:
    """|LowLevelApiDocstring|

    Verb: POST
    Endpoint: /api/sca/registries-configuration/projects/configuration/{configId}
    """
    url = urljoin(
        client.api_endpoint,
        f"sca/registries-configuration/projects/configuration/{configId}",
    )

    return await client.exec_request(requests.post, url, json=projectIds)

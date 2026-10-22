import requests
from cxone_api import CxOneClient
from cxone_api.util import join_query_dict
from requests.compat import urljoin
from typing import List


async def retrieve_configurations(client: CxOneClient, **kwargs) -> requests.Response:
    """|LowLevelApiDocstring|

    Verb: GET
    Endpoint: /api/sca/registries-configuration/configurations

    .. tip::
      This API returns results by pages.  When using cxone_api.util.page_generator, set
      the following parameters:

      * offset_param = "PageNumber"
      * offset_init_value = 1
      * offset_is_by_count = False

      Optional kwarg parameter PageSize is suggested to be set to 50
      rather than leave it at the default of 5.

    """
    url = urljoin(client.api_endpoint, "sca/registries-configuration/configurations")
    url = join_query_dict(url, kwargs)

    return await client.exec_request(requests.get, url)


async def create_configuration(
    client: CxOneClient, configurationName: str, packageManager: str, content: str
) -> requests.Response:
    """|LowLevelApiDocstring|

    Verb: POST
    Endpoint: /api/sca/registries-configuration/configurations
    """
    url = urljoin(client.api_endpoint, "sca/registries-configuration/configurations")
    payload = {
        "configurationName": configurationName,
        "packageManager": packageManager.value,
        "content": content,
    }

    return await client.exec_request(requests.post, url, json=payload)


async def retrieve_configuration(
    client: CxOneClient, configId: str
) -> requests.Response:
    """|LowLevelApiDocstring|

    Verb: GET
    Endpoint: /api/sca/registries-configuration/configurations/{configId}
    """
    url = urljoin(
        client.api_endpoint, f"sca/registries-configuration/configurations/{configId}"
    )

    return await client.exec_request(requests.get, url)


async def delete_configuration(client: CxOneClient, configId: str) -> requests.Response:
    """|LowLevelApiDocstring|

    Verb: DELETE
    Endpoint: /api/sca/registries-configuration/configurations/{configId}
    """
    url = urljoin(
        client.api_endpoint, f"sca/registries-configuration/configurations/{configId}"
    )

    return await client.exec_request(requests.delete, url)


async def modify_configuration(
    client: CxOneClient,
    configId: str,
    configurationName: str,
    packageManager: str,
    content: str,
) -> requests.Response:
    """|LowLevelApiDocstring|

    Verb: PATCH
    Endpoint: /api/sca/registries-configuration/configurations/{configId}
    """
    url = urljoin(
        client.api_endpoint, f"sca/registries-configuration/configurations/{configId}"
    )

    payload = {
        "configurationName": configurationName,
        "packageManager": packageManager,
        "content": content,
    }

    return await client.exec_request(requests.patch, url, json=payload)


async def retrieve_project_configuration(
    client: CxOneClient, projectId: str
) -> requests.Response:
    """|LowLevelApiDocstring|

    Verb: GET
    Endpoint: /api/sca/registries-configuration/configurations/project/{projectId}
    """
    url = urljoin(
        client.api_endpoint,
        f"sca/registries-configuration/configurations/project/{projectId}",
    )

    return await client.exec_request(requests.get, url)


async def associate_configurations_with_project(
    client: CxOneClient, projectId: str, configurationIds: List[str]
) -> requests.Response:
    """|LowLevelApiDocstring|

    Verb: POST
    Endpoint: /api/sca/registries-configuration/configurations/project/{projectId}
    """
    url = urljoin(
        client.api_endpoint,
        f"sca/registries-configuration/configurations/project/{projectId}",
    )

    return await client.exec_request(requests.post, url, json=configurationIds)


async def disassociate_configurations_from_project(
    client: CxOneClient, projectId: str, configurationIds: List[str]
) -> requests.Response:
    """|LowLevelApiDocstring|

    Verb: DELETE
    Endpoint: /api/sca/registries-configuration/configurations/project/{projectId}
    """
    url = urljoin(
        client.api_endpoint,
        f"sca/registries-configuration/configurations/project/{projectId}",
    )

    return await client.exec_request(requests.delete, url, json=configurationIds)


async def retrieve_configurations_with_tag(
    client: CxOneClient, tagId: str
) -> requests.Response:
    """|LowLevelApiDocstring|

    Verb: GET
    Endpoint: /api/sca/registries-configuration/configurations/tag/{tagId}
    """
    url = urljoin(
        client.api_endpoint, f"sca/registries-configuration/configurations/tag/{tagId}"
    )

    return await client.exec_request(requests.get, url)


async def associate_configurations_with_tag(
    client: CxOneClient, tagId: str, configurationIds: List[str]
) -> requests.Response:
    """|LowLevelApiDocstring|

    Verb: POST
    Endpoint: /api/sca/registries-configuration/configurations/tag/{tagId}
    """
    url = urljoin(
        client.api_endpoint, f"sca/registries-configuration/configurations/tag/{tagId}"
    )

    return await client.exec_request(requests.post, url, json=configurationIds)


async def disassociate_configurations_from_tag(
    client: CxOneClient, tagId: str
) -> requests.Response:
    """|LowLevelApiDocstring|

    Verb: DELETE
    Endpoint: /api/sca/registries-configuration/configurations/tag/{tagId}
    """
    url = urljoin(
        client.api_endpoint, f"sca/registries-configuration/configurations/tag/{tagId}"
    )

    return await client.exec_request(requests.delete, url)

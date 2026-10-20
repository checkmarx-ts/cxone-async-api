import requests
from cxone_api import CxOneClient
from cxone_api.util import join_query_dict
from requests.compat import urljoin
from typing import List


async def retrieve_list_of_configurations_by_tag(
    client: CxOneClient, **kwargs
) -> requests.Response:
    """|LowLevelApiDocstring|

    Verb: GET
    Endpoint: /api/sca/registries-configuration/tags

    This API returns results by pages.  When using cxone_api.util.page_generator, set
    the following parameters:

    * offset_param = "PageNumber"
    * offset_init_value = 1
    * offset_is_by_count = False

    Optional kwarg parameter PageSize is suggested to be set to 50
    rather than leave it at the default of 5.

    """
    url = urljoin(client.api_endpoint, "sca/registries-configuration/tags")
    url = join_query_dict(url, kwargs)

    return await client.exec_request(requests.get, url)


async def create_configuration_tag(client: CxOneClient, name: str) -> requests.Response:
    """|LowLevelApiDocstring|

    Verb: POST
    Endpoint: /api/sca/registries-configuration/tags
    """
    url = urljoin(client.api_endpoint, "sca/registries-configuration/tags")

    return await client.exec_request(requests.post, url, json={"name": name})


async def retrieve_tag_details(client: CxOneClient, tagId: str) -> requests.Response:
    """|LowLevelApiDocstring|

    Verb: GET
    Endpoint: /api/sca/registries-configuration/tags/{tagId}
    """
    url = urljoin(client.api_endpoint, f"sca/registries-configuration/tags/{tagId}")

    return await client.exec_request(requests.get, url)


async def modify_tag_name(
    client: CxOneClient, tagId: str, name: str
) -> requests.Response:
    """|LowLevelApiDocstring|

    Verb: PATCH
    Endpoint: /api/sca/registries-configuration/tags/{tagId}
    """
    url = urljoin(client.api_endpoint, f"sca/registries-configuration/tags/{tagId}")

    return await client.exec_request(requests.patch, url, json={"name": name})


async def delete_tag(client: CxOneClient, tagId: str) -> requests.Response:
    """|LowLevelApiDocstring|

    Verb: DELETE
    Endpoint: /api/sca/registries-configuration/tags/{tagId}
    """
    url = urljoin(client.api_endpoint, f"sca/registries-configuration/tags/{tagId}")

    return await client.exec_request(requests.delete, url)


async def retrieve_tags_of_configuration(
    client: CxOneClient, configId: str
) -> requests.Response:
    """|LowLevelApiDocstring|

    Verb: GET
    Endpoint: /api/sca/registries-configuration/tags/configuration/{configId}
    """
    url = urljoin(
        client.api_endpoint,
        f"sca/registries-configuration/tags/configuration/{configId}",
    )

    return await client.exec_request(requests.get, url)


async def associate_tags_with_configuration(
    client: CxOneClient, configId: str, tags: List[str]
) -> requests.Response:
    """|LowLevelApiDocstring|

    Verb: POST
    Endpoint: /api/sca/registries-configuration/tags/configuration/{configId}
    """
    url = urljoin(
        client.api_endpoint,
        f"sca/registries-configuration/tags/configuration/{configId}",
    )

    return await client.exec_request(requests.post, url, json=tags)


async def disassociate_all_tags_from_configuration(
    client: CxOneClient, configId: str
) -> requests.Response:
    """|LowLevelApiDocstring|

    Verb: DELETE
    Endpoint: /api/sca/registries-configuration/tags/configuration/{configId}
    """
    url = urljoin(
        client.api_endpoint,
        f"sca/registries-configuration/tags/configuration/{configId}",
    )

    return await client.exec_request(requests.delete, url)

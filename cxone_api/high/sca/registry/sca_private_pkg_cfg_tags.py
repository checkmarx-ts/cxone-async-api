from __future__ import annotations
from typing import Dict, List
from cxone_api import CxOneClient
from cxone_api.low.sca.registry.tags import (
    create_configuration_tag,
    retrieve_tag_details,
    modify_tag_name,
    delete_tag,
    retrieve_list_of_configurations_by_tag,
)
from .sca_basic_private_pkg_repo_cfg import BasicPackageRepositoryConfiguration
from cxone_api.util import json_on_ok, page_generator


class PackageRepositoryConfigurationTag:
    """A class representing a tag used to group SCA private package repository
    configurations.
    """

    @staticmethod
    async def create_new(
        client: CxOneClient, name: str
    ) -> PackageRepositoryConfigurationTag:
        """Creates a new configuration tag.

        :param client: The CxOneClient instance used to communicate with Checkmarx One.
        :type client: CxOneClient

        :param name: The name of the new tag.
        :type name: str

        :raises ResponseException: Raised if the tag could not be created.

        :return: The new tag with no associated configurations.
        :rtype: PackageRepositoryConfigurationTag
        """
        inst = PackageRepositoryConfigurationTag()
        new_tag = json_on_ok(await create_configuration_tag(client, name))
        inst.__client = client
        inst.__id = new_tag.get("id")
        inst.__name = name
        inst.__configurations = []
        return inst

    @staticmethod
    def from_tag_json(
        client: CxOneClient, json: Dict
    ) -> PackageRepositoryConfigurationTag:
        """Creates an instance from a tag JSON dictionary returned by the API.

        :param client: The CxOneClient instance used to communicate with Checkmarx One.
        :type client: CxOneClient

        :param json: The tag JSON dictionary.
        :type json: Dict

        :rtype: PackageRepositoryConfigurationTag
        """
        inst = PackageRepositoryConfigurationTag()
        inst.__id = json.get("id")
        inst.__name = json.get("name")
        inst.__client = client
        inst.__configurations = [
            BasicPackageRepositoryConfiguration.from_config_json(client, x)
            for x in json.get("configurations", [])
        ]
        return inst

    @staticmethod
    async def retrieve_by_id(
        client: CxOneClient, tagId: str
    ) -> PackageRepositoryConfigurationTag:
        """Loads a configuration tag by ID.

        :param client: The CxOneClient instance used to communicate with Checkmarx One.
        :type client: CxOneClient

        :param tagId: The ID of the tag to retrieve.
        :type tagId: str

        :raises ResponseException: Raised if the tag could not be retrieved.

        :rtype: PackageRepositoryConfigurationTag
        """
        return PackageRepositoryConfigurationTag.from_tag_json(
            client, json_on_ok(await retrieve_tag_details(client, tagId))
        )

    async def reload(self) -> PackageRepositoryConfigurationTag:
        """Reload a tag to get updated associations.

        :raises ResponseException: Raised if the tag could not be retrieved.

        :rtype: PackageRepositoryConfigurationTag
        """
        return await PackageRepositoryConfigurationTag.retrieve_by_id(self.__client, self.tagid)

    @staticmethod
    async def retrieve_by_name(
        client: CxOneClient, name: str
    ) -> List[PackageRepositoryConfigurationTag]:
        """Loads the package repository configuration tags by name.

        .. warning::
           This requires iteration of all existing tags.  Using this
           method is not performant.

        :param client: The CxOneClient instance used to communicate with Checkmarx One.
        :type client: CxOneClient

        :param name: The name of the configuration tag to retrieve.
        :type name: str

        :return: A list of private configuration tags matching ``name``.
            The list is empty if no tags match.

        :rtype: List[PackageRepositoryConfigurationTag]

        """
        result = []
        async for tag_json in page_generator(
            retrieve_list_of_configurations_by_tag,
            offset_param="PageNumber",
            offset_init_value=1,
            offset_is_by_count=False,
            client=client,
        ):
            tag_cfg = PackageRepositoryConfigurationTag.from_tag_json(client, tag_json)
            if tag_cfg.name == name:
                result.append(tag_cfg)

        return result

    def __repr__(self):
        return f"{self.tagid}:{self.name}:configs[{len(self.associated_configs)}]"

    def __eq__(self, other):
        return other is not None and self.tagid == other.tagid

    def __hash__(self):
        return hash(self.tagid)

    @property
    def name(self) -> str:
        """The name of the tag.

        :rtype: str
        """
        return self.__name

    @property
    def tagid(self) -> str:
        """The ID of the tag.

        :rtype: str
        """
        return self.__id

    @property
    def associated_configs(self) -> List[BasicPackageRepositoryConfiguration]:
        """The configurations associated with the tag at the time it was loaded.

        :rtype: List[BasicPackageRepositoryConfiguration]
        """
        return self.__configurations

    async def change_name(self, new_name: str) -> bool:
        """Changes the name of the tag.

        :param new_name: The new name of the tag.
        :type new_name: str

        :return: True if the name was changed, False otherwise.
        :rtype: bool
        """
        if (await modify_tag_name(self.__client, self.tagid, new_name)).ok:
            self.__name = new_name
            return True

        return False

    async def delete(self) -> bool:
        """Deletes the tag.

        :return: True if the tag was deleted, False otherwise.
        :rtype: bool
        """
        if (await delete_tag(self.__client, self.__id)).ok:
            return True

        return False

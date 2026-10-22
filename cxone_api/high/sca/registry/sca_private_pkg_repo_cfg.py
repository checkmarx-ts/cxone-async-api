from __future__ import annotations
import asyncio
from typing import List, Any, Dict
from .package_manager_types import PackageManagerType
from .sca_private_pkg_cfg_tags import PackageRepositoryConfigurationTag
from .sca_basic_private_pkg_repo_cfg import BasicPackageRepositoryConfiguration
from cxone_api import CxOneClient
from cxone_api.util import json_on_ok, page_generator
from cxone_api.exceptions import CommunicationException
from cxone_api.low.sca.registry.configurations import (
    create_a_configuration,
    disassociate_configurations_from_project,
    delete_configuration,
    associate_configurations_with_tag,
    retrieve_a_configuration,
    retrieve_configurations,
    retrieve_project_configuration,
    retrieve_configurations_with_tag,
)
from cxone_api.low.sca.registry.projects import (
    associate_projects_with_configuration,
    retrieve_projects_associated_with_configuration,
    disassociate_all_projects_from_configuration,
)
from cxone_api.low.sca.registry.tags import (
    retrieve_tags_of_configuration,
    associate_tags_with_configuration,
    disassociate_all_tags_from_configuration,
)


class PackageRepositoryConfiguration(BasicPackageRepositoryConfiguration):
    """A class representing an SCA private package repository configuration,
    including the projects and tags associated with the configuration.
    """

    def __repr__(self):
        return f"{self.configId}:{self.packageManager.value}:{self.name}:projects[{len(self.associated_projects)}]:tags[{len(self.associated_tags)}]"

    def __eq__(self, other):
        return self.configId == other.configId

    def __internal_init(
        self,
        client: CxOneClient,
        config_id: str,
        name: str,
        package_manager: PackageManagerType,
        content: str,
        projects: List[str],
        tags: List[PackageRepositoryConfigurationTag],
    ) -> None:
        super()._internal_init(client, config_id, name, package_manager, content)
        self.__projects = projects
        self.__tags = tags
        self.__lock = asyncio.Lock()

    @staticmethod
    async def retrieve_by_configid(
        client: CxOneClient, configId: str
    ) -> PackageRepositoryConfiguration:
        """Loads a package repository configuration by ID.

        :param client: The CxOneClient instance used to communicate with Checkmarx One.
        :type client: CxOneClient

        :param configId: The ID of the configuration to retrieve.
        :type configId: str

        :raises ResponseException: Raised if the configuration could not be retrieved.

        :rtype: PackageRepositoryConfiguration
        """
        return PackageRepositoryConfiguration.from_config_json(
            client, json_on_ok(await retrieve_a_configuration(client, configId))
        )

    @staticmethod
    async def from_basic_config(
        client: CxOneClient, basic_config: BasicPackageRepositoryConfiguration
    ) -> PackageRepositoryConfiguration:
        """Loads the full package repository configuration for a basic configuration.

        :param client: The CxOneClient instance used to communicate with Checkmarx One.
        :type client: CxOneClient

        :param basic_config: The basic configuration to load.
        :type basic_config: BasicPackageRepositoryConfiguration

        :raises ResponseException: Raised if the configuration could not be retrieved.

        :rtype: PackageRepositoryConfiguration
        """
        return await PackageRepositoryConfiguration.retrieve_by_configid(
            client, basic_config.configId
        )

    @staticmethod
    def from_config_json(
        client: CxOneClient, json: Dict
    ) -> PackageRepositoryConfiguration:
        """Creates an instance from a configuration JSON dictionary returned by the API.

        :param client: The CxOneClient instance used to communicate with Checkmarx One.
        :type client: CxOneClient

        :param json: The configuration JSON dictionary.
        :type json: Dict

        :rtype: PackageRepositoryConfiguration
        """
        inst = PackageRepositoryConfiguration()
        inst.__internal_init(
            client=client,
            config_id=json.get("id"),
            name=json.get("configurationName"),
            package_manager=PackageManagerType(json.get("packageManager")),
            content=json.get("content"),
            projects=[x.get("id") for x in json.get("projects", [])],
            tags=[
                PackageRepositoryConfigurationTag.from_tag_json(client, x)
                for x in json.get("tags", [])
            ],
        )

        return inst

    @staticmethod
    async def retrieve_by_name(
        client: CxOneClient, name: str
    ) -> List[PackageRepositoryConfiguration]:
        """Loads the package repository configurations by name.

        .. warning::
           This requires iteration of all existing configurations.  Using this
           method is not performant.

        :param client: The CxOneClient instance used to communicate with Checkmarx One.
        :type client: CxOneClient

        :param name: The name of the private package repository configurations to retrieve.
        :type name: str

        :return: A list of private package repository configurations matching ``name``.
            The list is empty if no configurations match.

        :rtype: List[PackageRepositoryConfiguration]

        """
        result = []

        async for cfg in page_generator(
            retrieve_configurations,
            offset_param="PageNumber",
            offset_init_value=1,
            offset_is_by_count=False,
            client=client,
        ):

            if cfg.get("configurationName", "") == name:
                result.append(
                    PackageRepositoryConfiguration.from_config_json(client, cfg)
                )

        return result

    @staticmethod
    async def retrieve_project_configurations(
        client: CxOneClient, projectId: str
    ) -> List[PackageRepositoryConfiguration]:
        """Loads the package repository configurations assigned to a project.

        :param client: The CxOneClient instance used to communicate with Checkmarx One.
        :type client: CxOneClient

        :param projectId: The ID of the project.
        :type projectId: str

        :raises ResponseException: Raised if the configurations could not be retrieved.

        :return: A list of configurations assigned to the project.  The list is empty
            if no configurations are assigned.
        :rtype: List[PackageRepositoryConfiguration]
        """

        result = []

        for cfg in json_on_ok(await retrieve_project_configuration(client, projectId)):
            result.append(PackageRepositoryConfiguration.from_config_json(client, cfg))

        return result

    @staticmethod
    async def retrieve_tag_configurations(
        client: CxOneClient, tag: PackageRepositoryConfigurationTag
    ) -> List[PackageRepositoryConfiguration]:
        """Loads the package repository configurations associated with a tag.

        :param client: The CxOneClient instance used to communicate with Checkmarx One.
        :type client: CxOneClient

        :param tag: The tag.
        :type tag: PackageRepositoryConfigurationTag

        :raises ResponseException: Raised if the configurations could not be retrieved.

        :return: A list of configurations associated with the tag.  The list is empty
            if no configurations are associated.
        :rtype: List[PackageRepositoryConfiguration]
        """
        result = []

        for cfg in json_on_ok(
            await retrieve_configurations_with_tag(client, tag.tagid)
        ):
            result.append(PackageRepositoryConfiguration.from_config_json(client, cfg))

        return result

    @staticmethod
    async def create_new(
        client: CxOneClient,
        name: str,
        packageManager: PackageManagerType,
        content: str,
        tags: List[PackageRepositoryConfigurationTag] = None,
    ) -> PackageRepositoryConfiguration:
        """Creates a new package repository configuration.

        :param client: The CxOneClient instance used to communicate with Checkmarx One.
        :type client: CxOneClient

        :param name: The name of the new configuration.
        :type name: str

        :param packageManager: The package manager type of the new configuration.
        :type packageManager: PackageManagerType

        :param content: The content of the new configuration.
        :type content: str

        :param tags: Tags to associate with the new configuration.  Defaults to None.
        :type tags: List[PackageRepositoryConfigurationTag], optional

        :raises ResponseException: Raised if the configuration could not be created
            or retrieved after creation.

        :rtype: PackageRepositoryConfiguration
        """
        new_cfg_result = json_on_ok(
            await create_a_configuration(client, name, packageManager, str(content))
        )

        inst = await PackageRepositoryConfiguration.retrieve_by_configid(
            client, new_cfg_result.get("id")
        )

        if tags is not None:
            await associate_tags_with_configuration(
                client, inst.configId, [x.tagid for x in tags]
            )

            await inst.__reload_tag_associations()

        return inst

    @property
    def associated_projects(self) -> List[str]:
        """The IDs of the projects associated with the configuration.

        :rtype: List[str]
        """
        return self.__projects

    @property
    def associated_tags(self) -> List[PackageRepositoryConfigurationTag]:
        """The tags associated with the configuration.

        :rtype: List[PackageRepositoryConfigurationTag]
        """
        return self.__tags

    async def __reload_project_associations(self):
        project_assoc = json_on_ok(
            await retrieve_projects_associated_with_configuration(
                self._client, self.configId
            )
        )

        async with self.__lock:
            self.__projects = []
            for entry in project_assoc:
                self.__projects.append(entry.get("id"))

    async def __reload_tag_associations(self):

        tag_assoc = json_on_ok(
            await retrieve_tags_of_configuration(self._client, self.configId)
        )

        async with self.__lock:
            self.__tags = []
            for entry in tag_assoc:
                self.__tags.append(
                    PackageRepositoryConfigurationTag.from_tag_json(self._client, entry)
                )

    async def refresh_associations(self):
        """Reloads the projects and tags associated with the configuration.

        :raises ResponseException: Raised if the associations could not be retrieved.
        """
        await self.__reload_tag_associations()
        await self.__reload_project_associations()

    async def associate_with_projects(self, projectIds: List[str]) -> bool:
        """Associates the configuration with projects.

        :param projectIds: The IDs of the projects to associate with the configuration.
        :type projectIds: List[str]

        :return: True if the projects were associated, False otherwise.
        :rtype: bool
        """
        try:
            await associate_projects_with_configuration(
                self._client, self.configId, projectIds
            )
        except CommunicationException:
            return False

        await self.__reload_project_associations()
        return True

    async def disassociate_from_project(self, projectId: str) -> bool:
        """Disassociates the configuration from a project.

        :param projectId: The ID of the project to disassociate from the configuration.
        :type projectId: str

        :return: True if the project was disassociated, False otherwise.
        :rtype: bool
        """
        if (
            await disassociate_configurations_from_project(
                self._client, projectId, [self.configId]
            )
        ).ok:
            await self.__reload_project_associations()
            return True
        return False

    async def associate_with_tag(self, tag: PackageRepositoryConfigurationTag) -> bool:
        """Associates the configuration with a tag.

        :param tag: The tag to associate with the configuration.
        :type tag: PackageRepositoryConfigurationTag

        :return: True if the tag was associated, False otherwise.
        :rtype: bool
        """
        if (
            await associate_configurations_with_tag(
                self._client, tag.tagid, [self.configId]
            )
        ).ok:
            await self.__reload_tag_associations()
            return True

        return False

    async def disassociate_all_projects(self) -> bool:
        """Disassociates the configuration from all projects.

        :return: True if the projects were disassociated, False otherwise.
        :rtype: bool
        """
        if (
            await disassociate_all_projects_from_configuration(
                self._client, self.configId
            )
        ).ok:
            await self.__reload_project_associations()
            return True
        return False

    async def disassociate_all_tags(self) -> bool:
        """Disassociates the configuration from all tags.

        :return: True if the tags were disassociated, False otherwise.
        :rtype: bool
        """
        disassociate_all_tags_from_configuration
        if (
            await disassociate_all_tags_from_configuration(self._client, self.configId)
        ).ok:
            await self.__reload_tag_associations()
            return True
        return False

    async def delete(self) -> bool:
        """Deletes the configuration.

        :return: True if the configuration was deleted, False otherwise.
        :rtype: bool
        """
        if (await delete_configuration(self._client, self.configId)).ok:
            async with self.__lock:
                self.__projects = []
                self.__tags = []
            return True
        return False

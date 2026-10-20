from __future__ import annotations
import asyncio
from typing import List, Any, Dict
from .package_manager_types import PackageManagerType
from .sca_private_pkg_cfg_tags import PackageRepositoryConfigurationTag
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


class PackageRepositoryConfiguration:

    def __repr__(self):
        return f"{self.configId}:{self.packageManager.value}:{self.name}:projects[{len(self.associated_projects)}]:tags[{len(self.associated_tags)}]"

    def __internal_init(
        self,
        client: CxOneClient,
        config_id: str,
        name: str,
        package_manager: PackageManagerType,
        content: Any,
        projects: List[str],
        tags: List[PackageRepositoryConfigurationTag],
    ) -> None:
        self.__client = client
        self.__id = config_id
        self.__name = name
        self.__type = package_manager
        self.__content = content
        self.__projects = projects
        self.__tags = tags
        self.__lock = asyncio.Lock()

    @staticmethod
    async def retrieve_by_configid(
        client: CxOneClient, configId: str
    ) -> PackageRepositoryConfiguration:
        return PackageRepositoryConfiguration.from_config_json(
            client, json_on_ok(await retrieve_a_configuration(client, configId))
        )

    @staticmethod
    def from_config_json(
        client: CxOneClient, json: Dict
    ) -> PackageRepositoryConfiguration:
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

        result = []

        for cfg in json_on_ok(await retrieve_project_configuration(client, projectId)):
            result.append(PackageRepositoryConfiguration.from_config_json(client, cfg))

        return result

    @staticmethod
    async def retrieve_tag_configurations(
        client: CxOneClient, tag: PackageRepositoryConfigurationTag
    ) -> List[PackageRepositoryConfiguration]:
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
        new_cfg = json_on_ok(
            await create_a_configuration(client, name, packageManager, content)
        )
        inst = PackageRepositoryConfiguration()
        inst.__internal_init(
            client=client,
            config_id=new_cfg.get("id"),
            name=name,
            package_manager=packageManager,
            content=content,
            projects=[],
            tags=[],
        )

        if tags is not None:
            await associate_tags_with_configuration(
                client, inst.configId, [x.tagid for x in tags]
            )

            await inst.__reload_tag_associations()

        return inst

    @property
    def configId(self) -> str:
        return self.__id

    @property
    def packageManager(self) -> PackageManagerType:
        return self.__type

    @property
    def name(self) -> str:
        return self.__name

    @property
    def content(self) -> str:
        return self.__content

    @property
    def associated_projects(self) -> List[str]:
        return self.__projects

    @property
    def associated_tags(self) -> List[PackageRepositoryConfigurationTag]:
        return self.__tags

    async def __reload_project_associations(self):
        project_assoc = json_on_ok(
            await retrieve_projects_associated_with_configuration(
                self.__client, self.__id
            )
        )

        async with self.__lock:
            self.__projects = []
            for entry in project_assoc:
                self.__projects.append(entry.get("id"))

    async def __reload_tag_associations(self):

        tag_assoc = json_on_ok(
            await retrieve_tags_of_configuration(self.__client, self.__id)
        )

        async with self.__lock:
            self.__tags = []
            for entry in tag_assoc:
                self.__tags.append(
                    PackageRepositoryConfigurationTag.from_tag_json(
                        self.__client, entry
                    )
                )

    async def refresh_associations(self):
        await self.__reload_tag_associations()
        await self.__reload_project_associations()

    async def associate_with_projects(self, projectIds: List[str]) -> bool:
        try:
            await associate_projects_with_configuration(
                self.__client, self.__id, projectIds
            )
        except CommunicationException:
            return False

        await self.__reload_project_associations()
        return True

    async def disassociate_from_project(self, projectId: str) -> bool:
        if (
            await disassociate_configurations_from_project(
                self.__client, projectId, [self.__id]
            )
        ).ok:
            await self.__reload_project_associations()
            return True
        return False

    async def associate_with_tag(self, tag: PackageRepositoryConfigurationTag) -> bool:
        if (
            await associate_configurations_with_tag(
                self.__client, tag.tagid, [self.__id]
            )
        ).ok:
            await self.__reload_tag_associations()
            return True

        return False

    async def disassociate_all_projects(self) -> bool:
        if (
            await disassociate_all_projects_from_configuration(self.__client, self.__id)
        ).ok:
            await self.__reload_project_associations()
            return True
        return False

    async def disassociate_all_tags(self) -> bool:
        disassociate_all_tags_from_configuration
        if (
            await disassociate_all_tags_from_configuration(self.__client, self.__id)
        ).ok:
            await self.__reload_tag_associations()
            return True
        return False

    async def delete(self) -> bool:
        if (await delete_configuration(self.__client, self.__id)).ok:
            async with self.__lock:
                self.__projects = []
                self.__tags = []
            return True
        return False

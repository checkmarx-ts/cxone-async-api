from __future__ import annotations
import asyncio
from dataclasses import dataclass
from .sca_private_pkg_repo_cfg import PackageRepositoryConfiguration
from .sca_private_pkg_cfg_tags import PackageRepositoryConfigurationTag
from .exceptions import DuplicatePackageManagerException
from cxone_api import CxOneClient
from cxone_api.util import page_generator
from cxone_api.low.projects import retrieve_list_of_projects
from typing import List, AsyncGenerator


@dataclass(frozen=True)
class AssigneeDescriptor:
    projectId: str
    projectName: str


@dataclass(frozen=True)
class AssignmentResults:
    assignees: List[AssigneeDescriptor]
    exceptions: List[Exception]


class AbstractProjectAssignment:
    def _internal_init(self, client: CxOneClient):
        self.__client = client

    @property
    def client(self) -> CxOneClient:
        return self.__client

    def _project_page_generator(self) -> AsyncGenerator:
        raise NotImplementedError(
            AbstractProjectAssignment._project_page_generator.__name__
        )

    async def execute_assignment(
        self, concurrent_threads: int = 2
    ) -> AssignmentResults:

        concurrency = asyncio.Semaphore(concurrent_threads)

        tasks = []
        async for project in self._project_page_generator():
            tasks.append(
                self._check_for_assign_selections(
                    AssigneeDescriptor(
                        projectId=project.get("id"), projectName=project.get("name")
                    ),
                    concurrency,
                )
            )

        task_results = await asyncio.gather(*tasks, return_exceptions=True)

        projects_to_assign = [
            x for x in task_results if isinstance(x, AssigneeDescriptor)
        ]

        if len(projects_to_assign) > 0:
            await self._process_project_assignments(projects_to_assign)

        return AssignmentResults(
            assignees=projects_to_assign,
            exceptions=[x for x in task_results if isinstance(x, Exception)],
        )

    async def _check_for_assign_selections(
        self, project: AssigneeDescriptor, semaphore: asyncio.Semaphore
    ) -> None:
        raise NotImplementedError(
            AbstractProjectAssignment._check_for_assign_selections.__name__
        )

    async def _process_project_assignments(
        self, projects: List[AssigneeDescriptor]
    ) -> bool:
        raise NotImplementedError(
            AbstractProjectAssignment._process_project_assignments.__name__
        )


class ProjectAssignmentDefaults(AbstractProjectAssignment):

    def by_project_name_match(
        self,
        name_regex: str,
    ):
        self.__generator_factory = lambda: page_generator(
            retrieve_list_of_projects,
            array_element="projects",
            client=self.client,
            name_regex=name_regex,
        )

    def by_project_names(
        self,
        names: List[str],
    ):
        self.__generator_factory = lambda: page_generator(
            retrieve_list_of_projects,
            array_element="projects",
            client=self.client,
            names=names,
        )

    def by_project_tag(
        self,
        tag_key: str,
    ):
        self.__generator_factory = lambda: page_generator(
            retrieve_list_of_projects,
            array_element="projects",
            client=self.client,
            tags_keys=[tag_key],
        )

    def _project_page_generator(self) -> AsyncGenerator:
        return self.__generator_factory()


class ProjectPrivateRepoAssignment(ProjectAssignmentDefaults):

    def _internal_init(
        self, client: CxOneClient, config: PackageRepositoryConfiguration
    ):
        super()._internal_init(client)
        self.__config = config

    async def _check_for_assign_selections(
        self, descriptor: AssigneeDescriptor, semaphore: asyncio.Semaphore
    ) -> str:

        async with semaphore:
            # Check if this config is already assigned.  If so, do nothing.
            if descriptor.projectId not in self.__config.associated_projects:
                assigned_configs = await PackageRepositoryConfiguration.retrieve_project_configurations(
                    self.client, descriptor.projectId
                )
                # 2nd check in case the current config's associated projects are not correct.
                if self.__config not in assigned_configs:
                    # Check there are no assigned configs of same type of package manager.
                    clashes = []
                    for cfg in assigned_configs:
                        if cfg.packageManager == self.__config.packageManager:
                            clashes.append(cfg)

                    if len(clashes) > 0:
                        raise DuplicatePackageManagerException.clash(
                            descriptor.projectId,
                            descriptor.projectName,
                            self.__config,
                            clashes,
                        )
                    else:
                        # Return project id for assignment
                        return descriptor

    async def _process_project_assignments(
        self, projects: List[AssigneeDescriptor]
    ) -> bool:
        return await self.__config.associate_with_projects(
            [x.projectId for x in projects]
        )

    @staticmethod
    def by_project_name_match(
        client: CxOneClient,
        name_regex: str,
        config: PackageRepositoryConfiguration,
    ) -> ProjectPrivateRepoAssignment:
        inst = ProjectPrivateRepoAssignment()
        inst._internal_init(client, config)
        ProjectAssignmentDefaults.by_project_name_match(inst, name_regex)
        return inst

    @staticmethod
    def by_project_names(
        client: CxOneClient,
        names: List[str],
        config: PackageRepositoryConfiguration,
    ):
        inst = ProjectPrivateRepoAssignment()
        inst._internal_init(client, config)
        ProjectAssignmentDefaults.by_project_names(inst, names)
        return inst

    @staticmethod
    def by_project_tag(
        client: CxOneClient,
        tag_key: str,
        config: PackageRepositoryConfiguration,
    ):
        inst = ProjectPrivateRepoAssignment()
        inst._internal_init(client, config)
        ProjectAssignmentDefaults.by_project_tag(inst, tag_key)
        return inst


class ProjectPrivateRepoTagAssignment(ProjectAssignmentDefaults):

    def _internal_init(
        self, client: CxOneClient, tag: PackageRepositoryConfigurationTag
    ):
        super()._internal_init(client)
        self.__tag = tag

    @staticmethod
    def by_project_name_match(
        client: CxOneClient,
        tag: PackageRepositoryConfigurationTag,
        name_regex: str,
    ):
        inst = ProjectPrivateRepoTagAssignment()
        inst._internal_init(client, tag)
        ProjectAssignmentDefaults.by_project_name_match(inst, name_regex)
        return inst

    @staticmethod
    def by_project_names(
        client: CxOneClient,
        tag: PackageRepositoryConfigurationTag,
        names: List[str],
    ):
        inst = ProjectPrivateRepoTagAssignment()
        inst._internal_init(client, tag)
        ProjectAssignmentDefaults.by_project_names(inst, names)
        return inst

    @staticmethod
    def by_project_tag(
        client: CxOneClient,
        tag: PackageRepositoryConfigurationTag,
        tag_key: str,
    ):
        inst = ProjectPrivateRepoTagAssignment()
        inst._internal_init(client, tag)
        ProjectAssignmentDefaults.by_project_tag(inst, tag_key)
        return inst

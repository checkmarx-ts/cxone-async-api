from __future__ import annotations
import asyncio
from dataclasses import dataclass
from .sca_private_pkg_repo_cfg import PackageRepositoryConfiguration
from .sca_private_pkg_cfg_tags import PackageRepositoryConfigurationTag
from .sca_basic_private_pkg_repo_cfg import BasicPackageRepositoryConfiguration
from .exceptions import DuplicatePackageManagerException
from cxone_api import CxOneClient
from cxone_api.util import page_generator
from cxone_api.high.exceptions import NameNotFoundException
from cxone_api.high.access_mgmt.user_mgmt import Groups
from cxone_api.low.projects import retrieve_list_of_projects
from cxone_api.low.sca.registry.projects import associate_projects_with_configuration
from pathlib import PurePosixPath
from typing import List, AsyncGenerator


@dataclass(frozen=True)
class AssigneeDescriptor:
    """A class that describes a project selected for assignment.

    :ivar projectId: The ID of the project.
    :vartype projectId: str

    :ivar projectName: The name of the project.
    :vartype projectName: str
    """

    projectId: str
    projectName: str


@dataclass(frozen=True)
class AssignmentResults:
    """A class that describes the results of executing an assignment.

    :ivar assignment_success: True if all selected projects were successfully
        assigned or no projects were selected for assignment.  False if the
        assignment failed.
    :vartype assignment_success: bool

    :ivar assignees: The projects selected for assignment.
    :vartype assignees: List[AssigneeDescriptor]

    :ivar exceptions: Exceptions raised while checking if selected projects
        could be assigned.  Projects that raised an exception are not assigned.
    :vartype exceptions: List[Exception]
    """

    assignment_success: bool
    assignees: List[AssigneeDescriptor]
    exceptions: List[Exception]


class AbstractProjectAssignment:
    """The base class for assigning SCA private package repository configurations
    to projects.
    """

    def _internal_init(self, client: CxOneClient):
        self.__client = client

    @property
    def client(self) -> CxOneClient:
        """The CxOneClient instance used to communicate with Checkmarx One.

        :rtype: CxOneClient
        """
        return self.__client

    def _project_page_generator(self) -> AsyncGenerator:
        raise NotImplementedError(
            AbstractProjectAssignment._project_page_generator.__name__
        )

    async def execute_assignment(
        self, concurrent_threads: int = 2
    ) -> AssignmentResults:
        """Selects the projects matching the assignment criteria and assigns
        the configurations to them.

        A project is not assigned if it already has a different configuration
        assigned for the same package manager type as a configuration being
        assigned.  The clash is reported in :py:attr:`AssignmentResults.exceptions`.
        Configurations already assigned to a project are not treated as clashes.

        :param concurrent_threads: The maximum number of concurrent API requests.
            Defaults to 2.
        :type concurrent_threads: int, optional

        :raises DuplicatePackageManagerException: Raised before any projects are
            selected if the configurations to assign are malformed.

        :raises NameNotFoundException: Raised before any projects are assigned if
            the assignment selects projects by a group path that does not match a group.

        :rtype: AssignmentResults
        """

        concurrency = asyncio.Semaphore(concurrent_threads)

        await self._precheck_exec(concurrency)

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

        assign_success = False
        if len(projects_to_assign) > 0:
            assign_success = await self._process_project_assignments(
                projects_to_assign, concurrency
            )
        else:
            assign_success = True

        return AssignmentResults(
            assignment_success=assign_success,
            assignees=projects_to_assign,
            exceptions=[x for x in task_results if isinstance(x, BaseException)],
        )

    async def _precheck_exec(self, semaphore: asyncio.Semaphore) -> None: ...

    async def _check_for_assign_selections(
        self, project: AssigneeDescriptor, semaphore: asyncio.Semaphore
    ) -> AssigneeDescriptor:
        raise NotImplementedError(
            AbstractProjectAssignment._check_for_assign_selections.__name__
        )

    async def _process_project_assignments(
        self, projects: List[AssigneeDescriptor], semaphore: asyncio.Semaphore
    ) -> bool:
        raise NotImplementedError(
            AbstractProjectAssignment._process_project_assignments.__name__
        )

    async def _validate_no_clashes(
        self,
        descriptor: AssigneeDescriptor,
        configs: List[BasicPackageRepositoryConfiguration],
        assigned_configs: List[PackageRepositoryConfiguration] = None,
    ) -> None:
        if assigned_configs is None:
            assigned_configs = (
                await PackageRepositoryConfiguration.retrieve_project_configurations(
                    self.client, descriptor.projectId
                )
            )

        assigned_managers = {}

        for x in assigned_configs:
            assigned_managers.setdefault(x.packageManager, []).append(x.configId)

        # Check there are no assigned configs of same type of package manager
        # that have no already been assigned.
        clashes = []
        for cfg in configs:
            if cfg.packageManager in assigned_managers.keys():
                if cfg.configId not in assigned_managers[cfg.packageManager]:
                    clashes.append(cfg)

        if len(clashes) > 0:
            raise DuplicatePackageManagerException.clash(
                descriptor.projectId,
                descriptor.projectName,
                clashes,
            )


class ProjectAssignmentDefaults(AbstractProjectAssignment):
    """A base class implementing the default project selection criteria for
    assignments.
    """

    def by_project_name_match(
        self,
        name_regex: str,
    ):
        """Selects projects with names matching a regular expression.

        :param name_regex: The regular expression used to match project names.
        :type name_regex: str
        """
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
        """Selects projects by name.

        :param names: The names of the projects to select.
        :type names: List[str]
        """
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
        """Selects projects that have a project tag with the given key.

        :param tag_key: The project tag key.
        :type tag_key: str
        """
        self.__generator_factory = lambda: page_generator(
            retrieve_list_of_projects,
            array_element="projects",
            client=self.client,
            tags_keys=[tag_key],
        )

    def by_group_path(
        self,
        group_path: str,
    ):
        """Selects projects assigned to the group with the given full path.

        The group is resolved when the assignment is executed.

        :param group_path: The full path of the group (e.g. ``/parent/child``).
            The leading ``/`` is optional.
        :type group_path: str
        """

        async def generator():
            path = str("/" / PurePosixPath(group_path))
            group = await Groups(self.client).get_by_full_path(path)

            # Never query projects without a group filter; it would select all projects.
            if group is None:
                raise NameNotFoundException(path)

            async for project in page_generator(
                retrieve_list_of_projects,
                array_element="projects",
                client=self.client,
                groups=group.id,
            ):
                yield project

        self.__generator_factory = generator

    def _project_page_generator(self) -> AsyncGenerator:
        return self.__generator_factory()


class ProjectPrivateRepoAssignment(ProjectAssignmentDefaults):
    """Assigns a single package repository configuration to selected projects.

    Create instances with one of the ``by_*`` static methods, then call
    :py:meth:`execute_assignment`.  Projects that already have the configuration
    assigned are not selected.
    """

    def _internal_init(
        self, client: CxOneClient, config: PackageRepositoryConfiguration
    ):
        super()._internal_init(client)
        self.__config = config

    async def _check_for_assign_selections(
        self, descriptor: AssigneeDescriptor, semaphore: asyncio.Semaphore
    ) -> AssigneeDescriptor:

        async with semaphore:
            # Check if this config is already assigned.  If so, do nothing.
            if descriptor.projectId not in self.__config.associated_projects:
                assigned_configs = await PackageRepositoryConfiguration.retrieve_project_configurations(
                    self.client, descriptor.projectId
                )
                # 2nd check in case the current config's associated projects are not correct.
                if self.__config not in assigned_configs:
                    await self._validate_no_clashes(
                        descriptor, [self.__config], assigned_configs
                    )
                    return descriptor

    async def _process_project_assignments(
        self, projects: List[AssigneeDescriptor], semaphore: asyncio.Semaphore
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
        """Creates an assignment that selects projects with names matching a
        regular expression.

        :param client: The CxOneClient instance used to communicate with Checkmarx One.
        :type client: CxOneClient

        :param name_regex: The regular expression used to match project names.
        :type name_regex: str

        :param config: The configuration to assign.
        :type config: PackageRepositoryConfiguration

        :rtype: ProjectPrivateRepoAssignment
        """
        inst = ProjectPrivateRepoAssignment()
        inst._internal_init(client, config)
        ProjectAssignmentDefaults.by_project_name_match(inst, name_regex)
        return inst

    @staticmethod
    def by_project_names(
        client: CxOneClient,
        names: List[str],
        config: PackageRepositoryConfiguration,
    ) -> ProjectPrivateRepoAssignment:
        """Creates an assignment that selects projects by name.

        :param client: The CxOneClient instance used to communicate with Checkmarx One.
        :type client: CxOneClient

        :param names: The names of the projects to select.
        :type names: List[str]

        :param config: The configuration to assign.
        :type config: PackageRepositoryConfiguration

        :rtype: ProjectPrivateRepoAssignment
        """
        inst = ProjectPrivateRepoAssignment()
        inst._internal_init(client, config)
        ProjectAssignmentDefaults.by_project_names(inst, names)
        return inst

    @staticmethod
    def by_project_tag(
        client: CxOneClient,
        tag_key: str,
        config: PackageRepositoryConfiguration,
    ) -> ProjectPrivateRepoAssignment:
        """Creates an assignment that selects projects that have a project tag
        with the given key.

        :param client: The CxOneClient instance used to communicate with Checkmarx One.
        :type client: CxOneClient

        :param tag_key: The project tag key.
        :type tag_key: str

        :param config: The configuration to assign.
        :type config: PackageRepositoryConfiguration

        :rtype: ProjectPrivateRepoAssignment
        """
        inst = ProjectPrivateRepoAssignment()
        inst._internal_init(client, config)
        ProjectAssignmentDefaults.by_project_tag(inst, tag_key)
        return inst

    @staticmethod
    def by_group_path(
        client: CxOneClient,
        group_path: str,
        config: PackageRepositoryConfiguration,
    ) -> ProjectPrivateRepoAssignment:
        """Creates an assignment that selects projects assigned to the group
        with the given full path.

        :param client: The CxOneClient instance used to communicate with Checkmarx One.
        :type client: CxOneClient

        :param group_path: The full path of the group (e.g. ``/parent/child``).
            The leading ``/`` is optional.
        :type group_path: str

        :param config: The configuration to assign.
        :type config: PackageRepositoryConfiguration

        :raises NameNotFoundException: Raised by
            :py:meth:`execute_assignment` if no group matches ``group_path``.

        :rtype: ProjectPrivateRepoAssignment
        """
        inst = ProjectPrivateRepoAssignment()
        inst._internal_init(client, config)
        ProjectAssignmentDefaults.by_group_path(inst, group_path)
        return inst


class ProjectPrivateRepoTagAssignment(ProjectAssignmentDefaults):
    """Assigns all package repository configurations associated with a
    configuration tag to selected projects.

    Create instances with one of the ``by_*`` static methods, then call
    :py:meth:`execute_assignment`.  The tag must not be associated with more
    than one configuration for the same package manager type.
    """

    def _internal_init(
        self, client: CxOneClient, tag: PackageRepositoryConfigurationTag
    ):
        super()._internal_init(client)
        self.__tag = tag
        self.__config_map = {}

        for cfg in self.__tag.associated_configs:
            if not cfg.packageManager in self.__config_map.keys():
                self.__config_map[cfg.packageManager] = [cfg]
            else:
                self.__config_map[cfg.packageManager].append(cfg)

    @staticmethod
    def by_project_name_match(
        client: CxOneClient,
        name_regex: str,
        tag: PackageRepositoryConfigurationTag,
    ) -> ProjectPrivateRepoTagAssignment:
        """Creates an assignment that selects projects with names matching a
        regular expression.

        :param client: The CxOneClient instance used to communicate with Checkmarx One.
        :type client: CxOneClient

        :param tag: The configuration tag with the configurations to assign.
        :type tag: PackageRepositoryConfigurationTag

        :param name_regex: The regular expression used to match project names.
        :type name_regex: str

        :rtype: ProjectPrivateRepoTagAssignment
        """
        inst = ProjectPrivateRepoTagAssignment()
        inst._internal_init(client, tag)
        ProjectAssignmentDefaults.by_project_name_match(inst, name_regex)
        return inst

    @staticmethod
    def by_project_names(
        client: CxOneClient,
        names: List[str],
        tag: PackageRepositoryConfigurationTag,
    ) -> ProjectPrivateRepoTagAssignment:
        """Creates an assignment that selects projects by name.

        :param client: The CxOneClient instance used to communicate with Checkmarx One.
        :type client: CxOneClient

        :param tag: The configuration tag with the configurations to assign.
        :type tag: PackageRepositoryConfigurationTag

        :param names: The names of the projects to select.
        :type names: List[str]

        :rtype: ProjectPrivateRepoTagAssignment
        """
        inst = ProjectPrivateRepoTagAssignment()
        inst._internal_init(client, tag)
        ProjectAssignmentDefaults.by_project_names(inst, names)
        return inst

    @staticmethod
    def by_project_tag(
        client: CxOneClient,
        tag_key: str,
        tag: PackageRepositoryConfigurationTag,
    ) -> ProjectPrivateRepoTagAssignment:
        """Creates an assignment that selects projects that have a project tag
        with the given key.

        :param client: The CxOneClient instance used to communicate with Checkmarx One.
        :type client: CxOneClient

        :param tag: The configuration tag with the configurations to assign.
        :type tag: PackageRepositoryConfigurationTag

        :param tag_key: The project tag key.
        :type tag_key: str

        :rtype: ProjectPrivateRepoTagAssignment
        """
        inst = ProjectPrivateRepoTagAssignment()
        inst._internal_init(client, tag)
        ProjectAssignmentDefaults.by_project_tag(inst, tag_key)
        return inst

    @staticmethod
    def by_group_path(
        client: CxOneClient,
        group_path: str,
        tag: PackageRepositoryConfigurationTag,
    ) -> ProjectPrivateRepoTagAssignment:
        """Creates an assignment that selects projects assigned to the group
        with the given full path.

        :param client: The CxOneClient instance used to communicate with Checkmarx One.
        :type client: CxOneClient

        :param group_path: The full path of the group (e.g. ``/parent/child``).
            The leading ``/`` is optional.
        :type group_path: str

        :param tag: The configuration tag with the configurations to assign.
        :type tag: PackageRepositoryConfigurationTag

        :raises NameNotFoundException: Raised by
            :py:meth:`execute_assignment` if no group matches ``group_path``.

        :rtype: ProjectPrivateRepoTagAssignment
        """
        inst = ProjectPrivateRepoTagAssignment()
        inst._internal_init(client, tag)
        ProjectAssignmentDefaults.by_group_path(inst, group_path)
        return inst

    async def _precheck_exec(self, semaphore: asyncio.Semaphore) -> None:
        # Tag can't have multiple package manager configs.
        for k in self.__config_map.keys():
            if len(self.__config_map[k]) > 1:
                raise DuplicatePackageManagerException.malformed_tag(self.__tag, k)

    async def _check_for_assign_selections(
        self, descriptor: AssigneeDescriptor, semaphore: asyncio.Semaphore
    ) -> AssigneeDescriptor:

        async with semaphore:
            await self._validate_no_clashes(descriptor, self.__tag.associated_configs)

            return descriptor

    async def _process_project_assignments(
        self, projects: List[AssigneeDescriptor], semaphore: asyncio.Semaphore
    ) -> bool:
        pids = [x.projectId for x in projects]

        async def assign(configid):
            async with semaphore:
                return (
                    await associate_projects_with_configuration(
                        self.client, configid, pids
                    )
                ).ok

        tasks = [
            assign(x.configId) for x in (await self.__tag.reload()).associated_configs
        ]

        return False not in (await asyncio.gather(*tasks))

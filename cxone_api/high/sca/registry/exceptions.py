from __future__ import annotations
from typing import List
from .package_manager_types import PackageManagerType
from .sca_basic_private_pkg_repo_cfg import BasicPackageRepositoryConfiguration
from .sca_private_pkg_cfg_tags import PackageRepositoryConfigurationTag
from .package_manager_types import PackageManagerType


class DuplicatePackageManagerException(Exception):
    """An exception indicating that more than one private package repository
    configuration for the same package manager type would apply to a project.
    """

    @staticmethod
    def clash(
        project_id: str,
        project_name: str,
        clashing: List[BasicPackageRepositoryConfiguration],
    ) -> DuplicatePackageManagerException:
        """Creates an exception indicating a project already has configurations assigned
        for the package manager types of the given configurations.

        :param project_id: The ID of the project.
        :type project_id: str

        :param project_name: The name of the project.
        :type project_name: str

        :param clashing: The configurations that clash with configurations already
            assigned to the project.
        :type clashing: List[BasicPackageRepositoryConfiguration]

        :rtype: DuplicatePackageManagerException
        """
        return DuplicatePackageManagerException(
            f"Clash with one or more package manager repository configurations assigned to project [{project_id}:{project_name}]: "
            + f"[{','.join([str(x) for x in clashing])}]"
        )

    @staticmethod
    def malformed_tag(
        tag: PackageRepositoryConfigurationTag, type: PackageManagerType
    ) -> DuplicatePackageManagerException:
        """Creates an exception indicating a tag is associated with more than one
        configuration for the same package manager type.

        :param tag: The malformed tag.
        :type tag: PackageRepositoryConfigurationTag

        :param type: The package manager type with duplicate configurations.
        :type type: PackageManagerType

        :rtype: DuplicatePackageManagerException
        """
        return DuplicatePackageManagerException(
            f"Tag [{tag}] is malformed given it has duplicate configurations for {type.value}"
        )

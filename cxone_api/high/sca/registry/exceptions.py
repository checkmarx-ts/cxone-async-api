from __future__ import annotations
from typing import List
from .package_manager_types import PackageManagerType
from .sca_basic_private_pkg_repo_cfg import BasicPackageRepositoryConfiguration
from .sca_private_pkg_cfg_tags import PackageRepositoryConfigurationTag
from .package_manager_types import PackageManagerType


class DuplicatePackageManagerException(Exception):

    @staticmethod
    def clash(
        project_id: str,
        project_name: str,
        clashing: List[BasicPackageRepositoryConfiguration],
    ) -> DuplicatePackageManagerException:
        return DuplicatePackageManagerException(
            f"Clash with one or more package manager repository configurations assigned to project [{project_id}:{project_name}]: "
            + f"[{','.join([str(x) for x in clashing])}]"
        )

    @staticmethod
    def malformed_tag(
        tag: PackageRepositoryConfigurationTag, type: PackageManagerType
    ) -> DuplicatePackageManagerException:
        return DuplicatePackageManagerException(
            f"Tag [{tag}] is malformed given it has duplicate configurations for {type.value}"
        )

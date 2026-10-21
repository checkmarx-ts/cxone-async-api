from __future__ import annotations
from typing import List
from .package_manager_types import PackageManagerType
from .sca_basic_private_pkg_repo_cfg import BasicPackageRepositoryConfiguration


class DuplicatePackageManagerException(Exception):

    @staticmethod
    def clash(
        project_id: str,
        project_name: str,
        config: BasicPackageRepositoryConfiguration,
        clashing: List[BasicPackageRepositoryConfiguration],
    ) -> DuplicatePackageManagerException:
        return DuplicatePackageManagerException(
            f"{config.packageManager.value} package manager clash for project [{project_id}:{project_name}]: {config} clashes with assigned configurations [{','.join([str(x) for x in clashing])}]"
        )

from __future__ import annotations
from typing import Dict, List
from cxone_api import CxOneClient
from .package_manager_types import PackageManagerType


class BasicPackageRepositoryConfiguration:
    """A class representing the basic attributes of an SCA private package
    repository configuration.

    This does not include the projects or tags associated with the configuration.
    Use :py:meth:`PackageRepositoryConfiguration.from_basic_config` to load the
    full configuration.
    """

    def __repr__(self):
        return f"{self.configId}:{self.packageManager.value}:{self.name}"

    def _internal_init(
        self,
        client: CxOneClient,
        config_id: str,
        name: str,
        package_manager: PackageManagerType,
        content: str,
    ) -> None:
        self.__client = client
        self.__id = config_id
        self.__name = name
        self.__type = package_manager
        self.__content = str(content)

    @staticmethod
    def from_config_json(
        client: CxOneClient, json: Dict
    ) -> BasicPackageRepositoryConfiguration:
        """Creates an instance from a configuration JSON dictionary returned by the API.

        :param client: The CxOneClient instance used to communicate with Checkmarx One.
        :type client: CxOneClient

        :param json: The configuration JSON dictionary.
        :type json: Dict

        :rtype: BasicPackageRepositoryConfiguration
        """
        inst = BasicPackageRepositoryConfiguration()
        inst._internal_init(
            client=client,
            config_id=json.get("id"),
            name=json.get("configurationName"),
            package_manager=PackageManagerType(json.get("packageManager")),
            content=json.get("content"),
        )

        return inst

    @property
    def _client(self) -> CxOneClient:
        return self.__client

    @property
    def configId(self) -> str:
        """The ID of the configuration.

        :rtype: str
        """
        return self.__id

    @property
    def packageManager(self) -> PackageManagerType:
        """The package manager type of the configuration.

        :rtype: PackageManagerType
        """
        return self.__type

    @property
    def name(self) -> str:
        """The name of the configuration.

        :rtype: str
        """
        return self.__name

    @property
    def content(self) -> str:
        """The content of the configuration.

        :rtype: str
        """
        return self.__content

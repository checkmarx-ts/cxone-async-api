from aenum import MultiValueEnum


class PackageManagerType(MultiValueEnum):
    """The package manager types supported by SCA private package repository configurations.

    The value of each member is the name of the package manager as used by the
    Checkmarx One API.
    """

    NUGET = "nuget", "nuget.config"
    MAVEN = "maven", "settings.xml"
    NPM = "npm", ".npmrc"
    PIP = "pip", "pip.conf"
    GRADLE = "gradle", "init.gradle"

    @property
    def config_file_name(self) -> str:
        """The name of the package manager's configuration file.

        :rtype: str
        """
        # pylint: disable=E1101
        return self.values[1]

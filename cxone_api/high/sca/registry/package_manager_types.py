from enum import Enum


class PackageManagerType(Enum):
    """The package manager types supported by SCA private package repository configurations."""

    NUGET = "nuget"
    MAVEN = "maven"
    NPM = "npm"
    PIP = "pip"
    GRADLE = "gradle"

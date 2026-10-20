from enum import Enum


class PackageManagerType(Enum):
    NUGET = "nuget"
    MAVEN = "maven"
    NPM = "npm"
    PIP = "pip"
    GRADLE = "gradle"

from .base import AbstractScaGQLOrderQuery


class ScaTenantPackages(AbstractScaGQLOrderQuery):
  """Retrieves a list of packages discovered in all scans for the CheckmarxOne tenant."""

  @property
  def _result_element(self) -> str:
    return "reportingPackages"

  @property
  def _query(self) -> str:
    return """
query (
$where: ReportingPackageModelFilterInput
$take: Int!
$skip: Int!
$order: [ReportingPackageModelSortInput!]
) {
reportingPackages(where: $where, take: $take, skip: $skip, order: $order) {
packageId
packageName
packageVersion
packageRepository
outdated
releaseDate
newestVersion
newestVersionReleaseDate
numberOfVersionsSinceLastUpdate
effectiveLicenses
licenses
projectName
projectId
scanId
aggregatedCriticalVulnerabilities
aggregatedHighVulnerabilities
aggregatedMediumVulnerabilities
aggregatedLowVulnerabilities
aggregatedNoneVulnerabilities
aggregatedCriticalSuspectedMalwares
aggregatedHighSuspectedMalwares
aggregatedMediumSuspectedMalwares
aggregatedLowSuspectedMalwares
aggregatedNoneSuspectedMalwares
relation
isDevDependency
isTest
isNpmVerified
isPluginDependency
isPrivateDependency
tags
scanDate
status
statusValue
isMalicious
usage
isFixAvailable
fixRecommendationVersion
pendingStatus
pendingStatusEndDate
groupIds
applicationIds
}
}    
    """



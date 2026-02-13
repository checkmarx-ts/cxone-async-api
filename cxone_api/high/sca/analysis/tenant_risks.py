from .base import AbstractScaGQLWhereQuery

class ScaTenantRisks(AbstractScaGQLWhereQuery):
  """Retrieves a list of open package risks for the CheckmarxOne tenant."""
  @property
  def _result_element(self) -> str:
    return "reportingRisks"

  @property
  def _query(self) -> str:
    return """
query (
$where: ReportingRiskModelFilterInput
$take: Int!
$skip: Int!
) {
reportingRisks(
where: $where
take: $take
skip: $skip
) {
scanId
projectId
severity
pendingSeverity
riskType
vulnerabilityId
packageId
packageName
packageVersion
projectName
vulnerabilityPublicationDate
score
pendingScore
state
pendingState
scanDate
epssPercentile
epss
isExploitable
exploitabilityReason
exploitabilityStatus
kevDataExists
exploitDbDataExist
epssDataExists
detectionDate
cwe
cweTitle
isFixAvailable
fixRecommendationVersion
groupIds
applicationIds
}
}
"""
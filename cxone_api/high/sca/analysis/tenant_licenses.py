from .base import AbstractScaGQLWhereQuery

class ScaTenantLicenses(AbstractScaGQLWhereQuery):
  """
  Retrieves a list of licenses discovered in all scans for the CheckmarxOne tenant.
  """
  @property
  def _result_element(self) -> str:
    return "reportingLicenses"

  @property
  def _query(self) -> str:
    return """
query (
$where: ReportingLicenseModelFilterInput
$take: Int!
$skip: Int!
) {
reportingLicenses(
where: $where
take: $take
skip: $skip
) {
state
pendingState
riskScore
licenseId
name
licenseFamily
riskLevel
copyLeftType
packageId
packageName
packageVersion
referenceType
projectId
scanId
projectName
groupIds
applicationIds
}
}
"""

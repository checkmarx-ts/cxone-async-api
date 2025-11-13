from cxone_api.client import CxOneClient
from cxone_api.high.reports.abstract_report import AbstractReportRequest
from enum import Enum
from typing import List, Dict

class Scanners(Enum):
  SAST = "sast"
  SCA = "sca"
  KICS = "kics"
  CONTAINERS = "containers"
  MICROENGINES = "microengines"


class AbstractScanReport(AbstractReportRequest):
  def __init__(self, client : CxOneClient, scan_id : str, project_id : str,
               branch_name : str = None, sections : List[Enum]=None, 
               scanners : List[Scanners]=None, **kwargs):

    super().__init__(client=client, **kwargs)
    self.__scan_id = scan_id
    self.__project_id = project_id
    self.__branch = branch_name
    self.__sections = None if sections is None or len(sections) > 0 else [x.value for x in sections]
    self.__scanners = None if scanners is None or len(scanners) > 0 else [x.value for x in scanners]

  @property
  def data(self) -> Dict:
    data_dict = {
      "scanId" : self.__scan_id,
      "projectId" : self.__project_id,
    }

    if self.__branch is not None:
      data_dict['branchName'] = self.__branch

    if self.__sections is not None:
      data_dict['sections'] = self.__sections

    if self.__scanners is not None:
      data_dict['scanners'] = self.__scanners

    if self.email is not None:
      data_dict['email'] = self.email
    
    return data_dict

class ImprovedScanReport(AbstractScanReport):
  class ReportSections(Enum):
    SCAN_INFORMATION = "scan-information"
    RESULTS_OVERVIEW = "results-overview"
    SCAN_RESULTS = "scan-results"
    RESOLVED_RESULTS = "resolved-results"
    CATEGORIES = "categories"
    VULNERABILITY_DETAILS = "vulnerability-details"

  def __init__(self, client : CxOneClient, scan_id : str, project_id : str,
               branch_name : str = None, sections : List[ReportSections]=None, 
               scanners : List[Scanners]=None, **kwargs):
    super().__init__(client, scan_id, project_id, branch_name, sections, scanners, report_name="improved-scan-report", **kwargs)


class LegacyScanReport(AbstractScanReport):
  class ReportSections(Enum):
    SCAN_SUMMARY = "ScanSummary"
    EXECUTIVE_SUMMARY = "ExecutiveSummary"
    SCAN_RESULTS = "ScanResults"

  def __init__(self, client : CxOneClient, scan_id : str, project_id : str, 
               branch_name : str = None, sections : List[ReportSections]=None, 
               scanners : List[Scanners]=None, **kwargs):
    super().__init__(client, scan_id, project_id, branch_name, sections, scanners, report_name="scan-report", **kwargs)


class ProjectReport(AbstractReportRequest):

  class Granularity(Enum):
    ALL = "all"
    DAILY = "daily"

  class Sections(Enum):
    PROJECT_INFORMATION = "Project"
    TOTAL_RESULTS_OVERVIEW = "TotalResultsOverview"
    SCAN_RESULTS_OVERVIEW = "ScanResultsOverview"
    TOP_TEN_VULNERABLE_FILES = "TopTenVulnerableFiles"
    RESOLVED_VULNERABILITIES_SEVERITY = "ResolvedVulnerabilitiesSeverity"
    RESOLVED_VULNERABILITIES_SCANNER = "ResolvedVulnerabilitiesScanner"
    RESULTS_TOTAL_COMBINED = "ResultsTotalCombined"
    RESULTS_TOTAL_BY_SCANNER = "ResultsTotalByScanner"

  def __init__(self, client : CxOneClient, project_id : str, from_date : str, to_date : str, granularity : Granularity, sections : List[Sections] = None):
    super().__init__(client, "project-report")
    self.__granularity = granularity.value
    self.__sections = None if sections is None else [x.value for x in sections]

class ApplicationList(AbstractReportRequest):
  def __init__(self, client : CxOneClient):
    super().__init__(client, "application-list")

class ProjectList(AbstractReportRequest):
  def __init__(self, client : CxOneClient, project_ids : List[str]):
    super().__init__(client, "project-list")
    self.__project_ids = project_ids

class ScanList(AbstractReportRequest):
  def __init__(self, client : CxOneClient, project_id : str):
    super().__init__(client, "scan-list")
    self.__project_id = project_id

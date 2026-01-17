from cxone_api.client import CxOneClient
from cxone_api.high.reports.abstract_report import AbstractReportRequest
from enum import Enum
from typing import List, Dict, Union

class Scanners(Enum):
  """An enumeration of types of scan engines."""
  SAST = "sast"
  SCA = "sca"
  KICS = "kics"
  CONTAINERS = "containers"
  MICROENGINES = "microengines"


class AbstractScanReport(AbstractReportRequest):
  def __init__(self, client : CxOneClient, scan_id : str, project_id : str,
               branch_name : str = None, sections : List[Enum]=None, 
               scanners : List[Scanners]=None, **kwargs):
    """AbstractScanReport implementations are AbstractReportRequest implementations that request scan report types.

    :param scan_id: The Checkmarx One scan id that is used to populate the report data.
    :type scan_id: str

    :param project_id: The Checkmarx One project id that holds the scan id.
    :type project_id: str

    :param branch_name: The name of the branch where the source code for the scan originated. Default is None.
    :type branch_name: str,optional

    :param sections: A list of report sections to include in the generated report. Default is All.
    :type sections: List[Enum],optional

    :param scanners: A list of engine results to include in the generated report. Default is All.
    :type scanners: List[Scanners],optional

    :param **kwargs: Keyword arguments passed to the base class.
    :type **kwargs: Dict
    """

    super().__init__(client=client, **kwargs)
    self.__scan_id = scan_id
    self.__project_id = project_id
    self.__branch = branch_name
    self.__sections = None if sections is None or len(sections) == 0 else [x.value for x in sections]
    self.__scanners = None if scanners is None or len(scanners) == 0 else [x.value for x in scanners]

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
    """An enumeration for sections of the report related to the outer class."""
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
    """An enumeration for sections of the report related to the outer class."""
    SCAN_SUMMARY = "ScanSummary"
    EXECUTIVE_SUMMARY = "ExecutiveSummary"
    SCAN_RESULTS = "ScanResults"

  def __init__(self, client : CxOneClient, scan_id : str, project_id : str, 
               branch_name : str = None, sections : List[ReportSections]=None, 
               scanners : List[Scanners]=None, **kwargs):
    super().__init__(client, scan_id, project_id, branch_name, sections, scanners, report_name="scan-report", **kwargs)


class ProjectReport(AbstractReportRequest):

  class Granularity(Enum):
    """An enumeration to control the granularity parameter when generating the report."""
    ALL = "all"
    DAILY = "daily"

  class Sections(Enum):
    """An enumeration for sections of the report related to the outer class."""
    PROJECT_INFORMATION = "Project"
    TOTAL_RESULTS_OVERVIEW = "TotalResultsOverview"
    SCAN_RESULTS_OVERVIEW = "ScanResultsOverview"
    TOP_TEN_VULNERABLE_FILES = "TopTenVulnerableFiles"
    RESOLVED_VULNERABILITIES_SEVERITY = "ResolvedVulnerabilitiesSeverity"
    RESOLVED_VULNERABILITIES_SCANNER = "ResolvedVulnerabilitiesScanner"
    RESULTS_TOTAL_COMBINED = "ResultsTotalCombined"
    RESULTS_TOTAL_BY_SCANNER = "ResultsTotalByScanner"

  def __init__(self, client : CxOneClient, project_id : str, from_date : str, to_date : str, granularity : Granularity, 
               results_limit : int = None, sections : List[Sections] = None, **kwargs):
    """ProjectReport is an AbstractReportRequest implementation used to request a project report.

    :param project_id: The Checkmarx One project id that will be used to populate the report data.
    :type project_id: str

    :param from_date: The start date for the project data used to populate the report.
    :type from_date: str

    :param to_date: The end date for the project data used to populate the report.
    :type to_date: str

    :param granularity: The data granularity type used when creating the report.
    :type granularity: Granularity

    :param results_limit: The limit of the number of results to include in the report.  The default is no limit.
    :type results_limit: int, optional
    
    :param sections: A list of report sections to include in the generated report. Default is All.
    :type sections: List[Sections],optional

    :param **kwargs: Keyword arguments passed to the base class.
    :type **kwargs: Dict
    """
    
    super().__init__(client, "project-report", **kwargs)
    self.__granularity = granularity.value
    self.__results_limit = results_limit
    self.__project_id = project_id
    self.__sections = None if sections is None else [x.value for x in sections]
    self.__from = from_date
    self.__to = to_date

  @property
  def additional_data(self) -> Dict:
    additional = {
      "granularity" : self.__granularity,
      "fromDate" : self.__from,
      "toDate" : self.__to
    }

    if self.__results_limit is not None:
      additional['resultsLimit'] = self.__results_limit

    return additional

  @property
  def data(self) -> Dict:
    data_dict = {
      "projectId" : self.__project_id,
    }

    if self.__sections is not None:
      data_dict['sections'] = self.__sections

    if self.email is not None:
      data_dict['email'] = self.email

    return data_dict


class ApplicationList(AbstractReportRequest):
  def __init__(self, client : CxOneClient, **kwargs):
    """ApplicationList is an AbstractReportRequest implementation used to request a list of applications.

    :param **kwargs: Keyword arguments passed to the base class.
    :type **kwargs: Dict
    """
    super().__init__(client, "application-list", **kwargs)

  @property
  def data(self) -> Dict:
    data_dict = {
      # At this time, this API has a bug that requires projectId
      # as an empty string.
      "projectId" : "", 
      }

    if self.email is not None:
      data_dict['email'] = self.email
    
    return data_dict

class ProjectList(AbstractReportRequest):
  def __init__(self, client : CxOneClient, project_ids : Union[None, List[str]], **kwargs):
    """ProjectList is an AbstractReportRequest implementation used to request a list of projects.

    :param project_ids: A list of project ids to include in the list or None to include all projects.
    :type project_ids: Union[None, List[str]]

    :param **kwargs: Keyword arguments passed to the base class.
    :type **kwargs: Dict
    """
    super().__init__(client, "project-list", **kwargs)
    self.__project_ids = project_ids if project_ids is not None else ""

  @property
  def data(self) -> Dict:
    data_dict = {
      "projectId" : self.__project_ids, 
      }

    if self.email is not None:
      data_dict['email'] = self.email
    
    return data_dict

class ScanList(AbstractReportRequest):
  def __init__(self, client : CxOneClient, project_id : str, branch_name : str = None, **kwargs):
    """ScanList is an AbstractReportRequest implementation used to request a list of scans.

    :param project_id: The Checkmarx One project id that will be used to populate the report data.
    :type project_id: str

    :param branch_name: The name of the branch used to limit the scans included in the report. Default is None.
    :type branch_name: str,optional
    
    :param **kwargs: Keyword arguments passed to the base class.
    :type **kwargs: Dict
    """

    super().__init__(client, "scan-list", **kwargs)
    self.__project_id = project_id
    self.__branch = branch_name

  @property
  def data(self) -> Dict:
    data_dict = {
      "projectId" : self.__project_id, 
      }

    if self.email is not None:
      data_dict['email'] = self.email

    if self.__branch is not None:
      data_dict['branchName'] = self.__branch
    
    return data_dict

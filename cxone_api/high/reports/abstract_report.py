from cxone_api.client import CxOneClient
from cxone_api.high.reports.exceptions import ReportConfigException
from typing import List, Dict
from enum import Enum

class ReportType(Enum):
  """An enumeration of types of report responses to generate."""
  UI = "ui"
  CLI = "cli"
  EMAIL = "email"

class AbstractReportRequest:
  """AbstractReportRequest is an abstract base class that is used to define a report request.
  
    :param client: An instance of the client implementation class.
    :type client: CxOneClient

    :param report_name: The name of the report to compile.  This is usually provided by a subclassed implementation.
    :type report_name: str

    :param report_type: The type of the report response to generate. This is typically passed via a kwarg from a
                        subclass constructor. Defaults to ReportType.CLI
    :type report_type: ReportType, optional

    :param email: A list of email addresses where the report will be emailed if the report type indicates an email report.
    :type email: List[str], optional

    Some of the above base class parameters are typically provided by the implementation.  The parameter list below
    shows the parameters used for this implementation of AbstractReportRequest.
  
  """

  def __init__(self, client : CxOneClient, report_name : str, report_type : ReportType = ReportType.CLI, email : List[str] = None):
    self.__name = report_name
    self.__client = client
    self.__type = report_type

    if report_type == ReportType.EMAIL and (email is None or len(email) == 0):
      raise ReportConfigException.email_list_required()

    self.__email = email

  @property
  def report_name(self) -> str:
    """The name of the type of report to request"""
    return self.__name

  @property
  def client(self) -> CxOneClient:
    """The instance of the Checkmarx One client used to communicate with the Checkmarx One API"""
    return self.__client
  
  @property
  def report_type(self) -> ReportType:
    """The type of report response to generate"""
    return self.__type.value

  @property
  def email(self) -> List[str]:
    """A list of email addresses that will receive this report"""
    return self.__email
  
  @property
  def data(self) -> Dict:
    """A property that is implemented by the subclass to return a JSON dictionary."""
    raise NotImplementedError("data")
  
  @property
  def additional_data(self) -> Dict:
    """A property that is optionally implemented by the subclass to return a JSON dictionary."""
    return {}

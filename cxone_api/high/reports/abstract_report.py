from cxone_api.client import CxOneClient
from cxone_api.high.reports.exceptions import ReportConfigException
from typing import List, Dict
from enum import Enum

class ReportType(Enum):
  UI = "ui"
  CLI = "cli"
  EMAIL = "email"

class AbstractReportRequest:


  def __init__(self, client : CxOneClient, report_name : str, report_type : ReportType = ReportType.CLI, email : List[str] = None):
    self.__name = report_name
    self.__client = client
    self.__type = report_type

    if report_type == ReportType.EMAIL and (email is None or len(email) == 0):
      raise ReportConfigException.email_list_required()

    self.__email = email

  @property
  def report_name(self) -> str:
    return self.__name

  @property
  def client(self) -> CxOneClient:
    return self.__client
  
  @property
  def report_type(self) -> ReportType:
    return self.__type.value

  @property
  def email(self) -> List[str]:
    return self.__email
  
  @property
  def data(self) -> Dict:
    raise NotImplementedError("data")

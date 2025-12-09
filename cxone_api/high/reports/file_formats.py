from cxone_api.high.reports.abstract_file_format import AbstractReportFileFormat
from cxone_api.high.reports.report_contents import *
from cxone_api.high.reports.exceptions import ReportException
from typing import Union, Dict
from requests import get


class PDFReport(AbstractReportFileFormat):
  """Downloads the requested report content as a PDF.
  
     Use the get_report static method to retrieve the report.  Not all report types can be rendered
     in PDF format.
  """
  @staticmethod
  async def get_report(content_type : Union[ImprovedScanReport, LegacyScanReport, ProjectReport], wait_timeout_seconds : int=300) -> bytearray:
    """Retrieves the PDF report content.

    :param content_type: The type of report to create.
    :type content_type: Union[ImprovedScanReport, LegacyScanReport, ProjectReport]

    :param wait_timeout_seconds: The number of seconds to wait for the server to render the report.
    :type wait_timeout_seconds: int

    :raises ReportException: Raised when retrieval of a report fails for any reason.
    
    :return: A bytearray representing the PDF.  The contents of the bytearray can be written to a file to persist the PDF.
    :rtype: bytearray
    """
    assert(type(content_type) in [ImprovedScanReport, LegacyScanReport, ProjectReport])
    return await (PDFReport("pdf", content_type, wait_timeout_seconds))._get_report()

  async def _download(self, url : str) -> bytearray:
    resp = await self.content_type.client.exec_request(get, url=url)
    if resp.ok:
      return resp.content
    else:
      raise ReportException.report_download_fail(url)

class CSVReport(AbstractReportFileFormat):
  """Downloads the requested report content in a CSV format.
  
     Use the get_report static method to retrieve the report.  Not all report types can be rendered
     in CSV format.
  """
  @staticmethod
  async def get_report(content_type : Union[ImprovedScanReport, LegacyScanReport, ApplicationList, ProjectList, ScanList], wait_timeout_seconds : int=300) -> str:
    """Retrieves the CSV report content.

    :param content_type: The type of report to create.
    :type content_type: Union[ImprovedScanReport, LegacyScanReport, ApplicationList, ProjectList, ScanList]

    :param wait_timeout_seconds: The number of seconds to wait for the server to render the report.
    :type wait_timeout_seconds: int

    :raises ReportException: Raised when retrieval of a report fails for any reason.
    
    :return: A string representing the CSV.
    :rtype: str
    """
    assert(type(content_type) in [ImprovedScanReport, LegacyScanReport, ApplicationList, ProjectList, ScanList])
    return await (CSVReport("csv", content_type, wait_timeout_seconds))._get_report()

  async def _download(self, url : str) -> str:
    resp = await self.content_type.client.exec_request(get, url=url)
    if resp.ok:
      return resp.text
    else:
      raise ReportException.report_download_fail(url)

class JSONReport(AbstractReportFileFormat):
  """Downloads the requested report content in a JSON format.
  
     Use the get_report static method to retrieve the report.  Not all report types can be rendered
     in JSON format.
  """

  @staticmethod
  async def get_report(content_type : Union[ImprovedScanReport, LegacyScanReport, ProjectReport], wait_timeout_seconds : int=300) -> Dict:
    """Retrieves the JSON report content.

    :param content_type: The type of report to create.
    :type content_type: Union[ImprovedScanReport, LegacyScanReport, ProjectReport]

    :param wait_timeout_seconds: The number of seconds to wait for the server to render the report.
    :type wait_timeout_seconds: int

    :raises ReportException: Raised when retrieval of a report fails for any reason.
    
    :return: A dictionary representing the JSON report content.
    :rtype: dict
    """
    assert(type(content_type) in [ImprovedScanReport, LegacyScanReport, ProjectReport])
    return await (JSONReport("json", content_type, wait_timeout_seconds))._get_report()

  async def _download(self, url : str) -> Dict:
    resp = await self.content_type.client.exec_request(get, url=url)
    if resp.ok:
      return resp.json()
    else:
      raise ReportException.report_download_fail(url)

from cxone_api.high.reports.abstract_file_format import AbstractReportFileFormat
from cxone_api.high.reports.report_contents import *
from cxone_api.high.reports.exceptions import ReportException
from typing import Union, Dict
from requests import get


class PDFReport(AbstractReportFileFormat):
  @staticmethod
  async def get_report(content_type : Union[ImprovedScanReport, LegacyScanReport, ProjectReport], wait_timeout_seconds=300) -> bytearray:
    assert(type(content_type) in [ImprovedScanReport, LegacyScanReport, ProjectReport])
    return await (PDFReport("pdf", content_type, wait_timeout_seconds))._get_report()

  async def _download(self, url : str) -> bytearray:
    resp = await self.content_type.client.exec_request(get, url=url)
    if resp.ok:
      return resp.content
    else:
      raise ReportException.report_download_fail(url)

class CSVReport(AbstractReportFileFormat):
  @staticmethod
  async def get_report(content_type : Union[ImprovedScanReport, LegacyScanReport, ApplicationList, ProjectList, ScanList], wait_timeout_seconds=300) -> str:
    assert(type(content_type) in [ImprovedScanReport, LegacyScanReport, ApplicationList, ProjectList, ScanList])
    return await (CSVReport("csv", content_type, wait_timeout_seconds))._get_report()

  async def _download(self, url : str) -> str:
    resp = await self.content_type.client.exec_request(get, url=url)
    if resp.ok:
      return resp.text
    else:
      raise ReportException.report_download_fail(url)

class JSONReport(AbstractReportFileFormat):
  @staticmethod
  async def get_report(content_type : Union[ImprovedScanReport, LegacyScanReport, ProjectReport], wait_timeout_seconds=300) -> Dict:
    assert(type(content_type) in [ImprovedScanReport, LegacyScanReport, ProjectReport])
    return await (JSONReport("json", content_type, wait_timeout_seconds))._get_report()

  async def _download(self, url : str) -> Dict:
    resp = await self.content_type.client.exec_request(get, url=url)
    if resp.ok:
      return resp.json()
    else:
      raise ReportException.report_download_fail(url)

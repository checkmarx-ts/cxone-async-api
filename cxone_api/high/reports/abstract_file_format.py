from cxone_api.high.reports.abstract_report import AbstractReportRequest
from cxone_api.low.reports import create_a_report, retrieve_report_status
from cxone_api.high.reports.exceptions import ReportException
from cxone_api.util import json_on_ok
from requests import Response
from typing import Any
from time import perf_counter
import asyncio

class AbstractReportFileFormat:
  __SLEEP_MAX_SECONDS = 10
  __SLEEP_INCREMENT_SECONDS = 1

  def __init__(self, file_format : str, content_type : AbstractReportRequest, timeout_seconds : int):
    self.__format = file_format
    self.__content = content_type
    self.__timeout = timeout_seconds

  @property
  def file_format(self) -> str:
    return self.__format
  
  @property
  def content_type(self) -> AbstractReportRequest:
    return self.__content
  
  async def _create(self) -> Response:
    request_payload = {
      "reportName" : self.__content.report_name,
      "fileFormat" : self.file_format,
      "reportType" : self.__content.report_type,
      "data" : self.__content.data
    }

    return await create_a_report(self.__content.client, **request_payload)
  
  async def _download(self, url : str) -> Any:
    raise NotImplementedError("_download")
  
  async def _get_report(self) -> Any:
    create_response = await self._create()

    if not create_response.ok:
      raise ReportException.error_on_create(create_response)
    report_id = create_response.json()['reportId']

    start = perf_counter()
    sleep = AbstractReportFileFormat.__SLEEP_INCREMENT_SECONDS
    while perf_counter() - start < self.__timeout:
      await asyncio.sleep(min(sleep, AbstractReportFileFormat.__SLEEP_MAX_SECONDS))

      status_response = json_on_ok(await retrieve_report_status(self.__content.client, report_id))
      
      if status_response['status'] == "failed":
        raise ReportException.report_gen_fail()
      elif status_response['status'] == "completed":
        break
      
      sleep += AbstractReportFileFormat.__SLEEP_INCREMENT_SECONDS

    return await self._download(status_response['url'])




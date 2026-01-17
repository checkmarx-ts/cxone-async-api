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
    """Using the constructor is not necessary; the subclass will implement a static method that calls the constructor.
    
    :param file_format: The name of the file format sent to the API.  This is usually provided by the implementation.
    :type file_format: str

    :param content_type: The requested type of report content.
    :type content_type: AbstractReportRequest

    :param timeout_seconds: The number of seconds to wait for the server to generate a report before raising an exception.
    :type timeout_seconds: int
    
    """
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
    request_payload.update(self.__content.additional_data)

    return await create_a_report(self.__content.client, **request_payload)
  
  async def _download(self, url : str) -> Any:
    raise NotImplementedError("_download")
  
  async def _get_report(self) -> Any:
    create_response = await self._create()

    response_json = json_on_ok(create_response, [202, 400, 401, 403])

    if not create_response.ok:
      raise ReportException.error_on_create(response_json.get("message", f"{create_response.status_code}"))
    
    report_id = response_json['reportId']

    start = perf_counter()
    sleep = AbstractReportFileFormat.__SLEEP_INCREMENT_SECONDS
    timed_out = True
    while perf_counter() - start < self.__timeout:
      await asyncio.sleep(min(sleep, AbstractReportFileFormat.__SLEEP_MAX_SECONDS))

      status_response = json_on_ok(await retrieve_report_status(self.__content.client, report_id))
      
      if status_response['status'] == "failed":
        raise ReportException.report_gen_fail(self.__content.data)
      elif status_response['status'] == "completed":
        timed_out = False
        break
      
      sleep += AbstractReportFileFormat.__SLEEP_INCREMENT_SECONDS
    
    if timed_out:
      raise ReportException.report_gen_timeout(self.__content.data)


    return await self._download(status_response['url'])




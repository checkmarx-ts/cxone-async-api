from cxone_api import CxOneClient
from cxone_api.exceptions import ResponseException
from cxone_api.util import json_on_ok
from ..low.sca import request_scan_report, get_scan_report_status, retrieve_scan_report
import requests, enum
from typing import List
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from time import perf_counter, sleep


class ScaReportType(enum.Enum):
  """An enumeration indicating the type of SCA report requested."""
  CycloneDxJson = "CycloneDxJson"
  CycloneDxXml = "CycloneDxXml"
  SpdxJson = "SpdxJson"
  RemediatedPackagesJson = "RemediatedPackagesJson"
  ScanReportJson = "ScanReportJson"
  ScanReportXml = "ScanReportXml"
  ScanReportCsv = "ScanReportCsv"
  ScanReportPdf = "ScanReportPdf"


@dataclass_json
@dataclass(frozen=True)
class ScaReportParameters:
  """Parameters to control the produced SCA report."""
  hideDevAndTestDependencies : bool = False
  showOnlyEffectiveLicenses : bool = False
  excludePackages : bool = False
  excludeLicenses : bool = False
  excludeVulnerabilities : bool = False
  excludePolicies : bool = False
  filePaths : List[str] = field(default_factory=list)
  compressOutput : bool = False 

@dataclass_json
@dataclass(frozen=True)
class ScaReportOptions:
  """Configuration options for SCA reports."""
  fileFormat : ScaReportType = field(metadata=config(encoder=lambda x: x.name))
  exportParameters : ScaReportParameters = field(default_factory=ScaReportParameters)


async def get_sca_report(client : CxOneClient, scanId : str, reportOptions : ScaReportOptions, timeout_seconds : float = 300.0) -> requests.Response:
  """Retrieves an SCA scan report.

  :param client: The CxOneClient instance used to communicate with Checkmarx One
  :type client: CxOneClient

  :param scanid: The scan id with SCA results that will be used to produce the report.
  :type scanid: str

  :param reportOptions: Options that control the SCA report.
  :type reportOptions: ScaReportOptions

  :param timeout_seconds: The number of seconds to wait for the report to be produced before raising an exception to indicate failure.
  :type timeout_seconds: float

  :raises ResponseException: An exception that indicates failure to retrieve the report for any reason.
  :rtype: Response

  """
  args = { "scanId" : scanId}
  args.update(reportOptions.to_dict())
  response = json_on_ok(await request_scan_report(client, **args))
  exportId = response['exportId']

  loop_timer = cur_timer = perf_counter()
  delay_secs = 5
  ready = False

  while cur_timer - loop_timer <= timeout_seconds + delay_secs:
      cur_timer = perf_counter()

      status = json_on_ok(await get_scan_report_status(client, exportId))
      if status['exportStatus'] == "Completed":
          ready = True
          break
      sleep(delay_secs)
      delay_secs *= 2
  
  if not ready:
      raise ResponseException(f"Unable to retrieve SCA scan report after {int(cur_timer - loop_timer)} seconds")
  
  return await retrieve_scan_report(client, exportId)


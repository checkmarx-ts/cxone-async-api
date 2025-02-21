from .. import CxOneClient
from typing import Self
from ..low.scans import retrieve_scan_details
from .scans import ScanInspector
from ..util import json_on_ok
from ..low.misc import retrieve_versions
from dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass(frozen=True)
class CxOneVersions:
  CxOne : str
  SAST : str
  KICS : str

  async def factory(client : CxOneClient) -> Self:
    v = json_on_ok(await retrieve_versions(client))
    return CxOneVersions(CxOne=v["CxOne"], SAST=v["SAST"], KICS=v["KICS"])

async def scan_inspector_factory (client : CxOneClient, scanid : str) -> ScanInspector:
    scan = json_on_ok(await retrieve_scan_details(client, scanid))
    return ScanInspector(scan)



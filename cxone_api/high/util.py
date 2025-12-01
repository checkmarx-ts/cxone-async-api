from .. import CxOneClient
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

  @staticmethod
  async def factory(client : CxOneClient):
    """Creates an instance of CxOneVersions

        :param client: The CxOneClient instance used to communicate with Checkmarx One
        :type client: CxOneClient

        :rtype: CxOneVersions
    
    """
    v = json_on_ok(await retrieve_versions(client))
    return CxOneVersions(CxOne=v["CxOne"], SAST=v["SAST"], KICS=v["KICS"])

async def scan_inspector_factory (client : CxOneClient, scanid : str) -> ScanInspector:
    """Creates an instance of ScanInspector for the provided Scan Id

        :param client: The CxOneClient instance used to communicate with Checkmarx One
        :type client: CxOneClient

        :param scanid: The scan id to be inspected.
        :type scanid: str

        :rtype: ScanInspector
        
    """
    scan = json_on_ok(await retrieve_scan_details(client, scanid))
    return ScanInspector(scan)



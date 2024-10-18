from .. import CxOneClient
from ..low.scans import retrieve_scan_details
from .scans import ScanInspector
from ..util import json_on_ok


async def scan_inspector_factory (client : CxOneClient, scanid : str) -> ScanInspector:
    scan = json_on_ok(await retrieve_scan_details(client, scanid))
    return ScanInspector(scan)



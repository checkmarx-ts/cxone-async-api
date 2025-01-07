from typing import List, Dict
from .base_config import BaseScanConfiguration
from ...client import CxOneClient
from ..util import json_on_ok
from ...exceptions import ResponseException
from ...low.scan_configuration import \
  retrieve_tenant_configuration, update_tenant_configuration, delete_tenant_configuration, \
  retrieve_project_configuration, update_project_configuration, delete_project_configuration, \
  retrieve_scan_configuration


class TenantScanConfiguration(BaseScanConfiguration):

  def __init__(self, client : CxOneClient):
    super().__init__(client)

  def _origin_level(self) -> str:
    return "Tenant"

  async def _load_config(self) -> List[Dict]:
    return json_on_ok(await retrieve_tenant_configuration(self.client))

  async def _write_config(self, items : List[Dict]) -> None:
    resp = await update_tenant_configuration(self.client, items)
    if not resp.ok:
      raise ResponseException(resp)

  async def _write_deletes(self, keys : List[str]) -> None:
    resp = await delete_tenant_configuration(self.client, config_keys=','.join(keys))
    if not resp.ok:
      raise ResponseException(resp)

class ProjectScanConfiguration(BaseScanConfiguration):
  def __init__(self, client : CxOneClient, project_id : str):
    super().__init__(client)
    self.__project_id = project_id

  def _origin_level(self) -> str:
    return "Project"

class ScanConfiguration(ProjectScanConfiguration):
  def __init__(self, client : CxOneClient, project_id : str, scan_id : str):
    super().__init__(client, project_id)
    self.__scan_id = scan_id

  def _origin_level(self) -> str:
    return "Scan"

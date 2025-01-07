from .element_handler import CxOneConfigElementHandler
from ...exceptions import ConfigurationException, CommunicationException
from ...low.misc import retrieve_preset_list
from ..util import json_on_ok
from typing import Any, Type, List, Awaitable, Union
from .value_types import ScanLanguageMode, RestListEnum
import asyncio

class BaseConfigurationCategory:
  def __init__(self, container : CxOneConfigElementHandler):
    self.__config = container
  
  @property
  def _config(self) -> CxOneConfigElementHandler:
    return self.__config


class ConfigurationPropertyHandler:

  def __init__(self, handler : CxOneConfigElementHandler, prop_key : str, value_type : Union[Type, RestListEnum]):
    self.__handler = handler
    self.__key = prop_key
    self.__value_type = value_type

  def __convert_from(self, value : Any) -> Any:
    if isinstance(self.__value_type, RestListEnum):
      return str(value)

    if self.__value_type is bool:
      if isinstance(value, str):
        return (not value == '') or bool(value)
      else:
        return bool(value)
    else:
      return value

  def __convert_to(self, value : Any) -> Any:
    if self.__value_type is bool:
      return str(bool(value)).lower()
    
    if self.__value_type is str and not isinstance(value, str):
      return str(value)
    
    return value
  

  async def setValue(self, value : Any) -> None:
    if isinstance(self.__value_type, RestListEnum):
      if not await self.__value_type.is_valid(value):
        raise ConfigurationException.not_in_enum(value, await self.__value_type.get_enum())
    elif not isinstance(value, self.__value_type) and \
      not isinstance(self.__value_type(value), self.__value_type):
      raise ConfigurationException.wrong_type(value, self.__value_type)

    await self.__handler._set_value(self.__key, self.__convert_to(value))

  async def getValue(self) -> Any:
    return self.__convert_from(await self.__handler._get_value(self.__key))

  async def setOverride(self, value : bool) -> None:
    await self.__handler._set_override(self.__key, value)

  async def getOverride(self) -> bool:
    return await self.__handler._get_override(self.__key)

  async def reset(self) -> None:
    await self.__handler._delete_config(self.__key)


class SastPresetType(RestListEnum):

  def __init__(self, retrieve_lambda : Awaitable[List[str]]):
    super().__init__()
    self.__get_lambda = retrieve_lambda
    self.__lock = asyncio.Lock()
    self.__enum = None

  async def get_enum(self) -> List[str]:
    async with self.__lock:
      if self.__enum == None:
        self.__enum = await self.__get_lambda()

    return self.__enum


class SastScanConfig(BaseConfigurationCategory):
  def __init__(self, container : CxOneConfigElementHandler):
    super().__init__(container)
    self.__fastscan = ConfigurationPropertyHandler(self._config, "scan.config.sast.fastScanMode", bool)
    self.__exclusions = ConfigurationPropertyHandler(self._config, "scan.config.sast.filter", str)
    self.__incremental = ConfigurationPropertyHandler(self._config, "scan.config.sast.incremental", bool)
    self.__rec = ConfigurationPropertyHandler(self._config, "scan.config.sast.recommendedExclusions", bool)
    self.__verbose = ConfigurationPropertyHandler(self._config, "scan.config.sast.engineVerbose", bool)
    self.__mode = ConfigurationPropertyHandler(self._config, "scan.config.sast.languageMode", ScanLanguageMode)

    async def get_presets() -> List[str]:
      pl_resp = await retrieve_preset_list(self._config.client)
      if not pl_resp.ok:
        raise CommunicationException(pl_resp)
      
      pl = json_on_ok(pl_resp)

      return [x['name'] for x in pl]

    self.__preset = ConfigurationPropertyHandler(self._config, "scan.config.sast.presetName", 
                                                 SastPresetType(get_presets))

  @property
  def FastScan(self) -> ConfigurationPropertyHandler:
    return self.__fastscan
  
  @property
  def Exclusions(self) -> ConfigurationPropertyHandler:
    return self.__exclusions

  @property
  def IncrementalScan(self) -> ConfigurationPropertyHandler:
    return self.__incremental

  @property
  def Preset(self) -> ConfigurationPropertyHandler:
    return self.__preset

  @property
  def RecommendedExclusions(self) -> ConfigurationPropertyHandler:
    return self.__rec

  @property
  def EngineVerbose(self) -> ConfigurationPropertyHandler:
    return self.__verbose

  @property
  def LanguageMode(self) -> ConfigurationPropertyHandler:
    return self.__mode

class ScaScanConfig(BaseConfigurationCategory):
  def __init__(self, container : CxOneConfigElementHandler):
    super().__init__(container)
    self.__exclusions = ConfigurationPropertyHandler(self._config, "scan.config.sca.filter", str)
    self.__obs_pattern = ConfigurationPropertyHandler(self._config, "scan.config.sca.obfuscatePackagesPattern", str)
    self.__exp_path = ConfigurationPropertyHandler(self._config, "scan.config.sca.ExploitablePath", bool)
    self.__exp_path_days = ConfigurationPropertyHandler(self._config, "scan.config.sca.LastSastScanTime", str)

  @property
  def Exclusions(self) -> ConfigurationPropertyHandler:
    return self.__exclusions

  @property
  def ObfuscatePackagesPattern(self) -> ConfigurationPropertyHandler:
    return self.__obs_pattern

  @property
  def ExploitablePath(self) -> ConfigurationPropertyHandler:
    return self.__exp_path

  @property
  def ExploitablePathLastScanDays(self) -> ConfigurationPropertyHandler:
    return self.__exp_path_days

class ApiSecurityScanConfig(BaseConfigurationCategory):
  def __init__(self, container : CxOneConfigElementHandler):
    super().__init__(container)
    self.__exclusions = ConfigurationPropertyHandler(self._config, "scan.config.apisec.swaggerFilter", str)

  @property
  def SwaggerFilter(self) -> ConfigurationPropertyHandler:
    return self.__exclusions

class ContainerScanConfig(BaseConfigurationCategory):
  def __init__(self, container : CxOneConfigElementHandler):
    super().__init__(container)
    self.__exclusions = ConfigurationPropertyHandler(self._config, "scan.config.containers.filesFilter", str)
    self.__package_filter = ConfigurationPropertyHandler(self._config, "scan.config.containers.packagesFilter", str)
    self.__img_tag_filter = ConfigurationPropertyHandler(self._config, "scan.config.containers.imagesFilter", str)
    self.__exclude_non_final = ConfigurationPropertyHandler(self._config, "scan.config.containers.nonFinalStagesFilter", bool)

  @property
  def Exclusions(self) -> ConfigurationPropertyHandler:
    return self.__exclusions

  @property
  def ImageTagFilter(self) -> ConfigurationPropertyHandler:
    return self.__img_tag_filter

  @property
  def PrivatePackageFilter(self) -> ConfigurationPropertyHandler:
    return self.__package_filter

  @property
  def ExclusionNonFinalStagesFilter(self) -> ConfigurationPropertyHandler:
    return self.__exclude_non_final

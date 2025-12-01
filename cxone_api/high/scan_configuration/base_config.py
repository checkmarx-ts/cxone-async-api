from .categories import SastScanConfig, ScaScanConfig, ApiSecurityScanConfig, ContainerScanConfig
from .element_handler import CxOneConfigElementHandler
from ...client import CxOneClient


class BaseScanConfiguration(CxOneConfigElementHandler):
  def __init__(self, client : CxOneClient):
    super().__init__(client)
    self.__sast = SastScanConfig(self)
    self.__sca = ScaScanConfig(self)
    self.__api = ApiSecurityScanConfig(self)
    self.__containers = ContainerScanConfig(self)
  
  @property
  def SAST(self) -> SastScanConfig:
    """The SAST scan configuration for the class instance scope level."""
    return self.__sast

  @property
  def SCA(self) -> ScaScanConfig:
    """The SCA scan configuration for the class instance scope level."""
    return self.__sca

  @property
  def APISec(self) -> ApiSecurityScanConfig:
    """The APISec scan configuration for the class instance scope level."""
    return self.__api

  @property
  def Containers(self) -> ContainerScanConfig:
    """The Containers scan configuration for the class instance scope level."""
    return self.__containers

  def _origin_level(self) -> str:
    raise NotImplementedError("_origin_level")

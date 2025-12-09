import asyncio
from typing import List, Dict, Any
from ...client import CxOneClient

class CxOneConfigElementHandler:
  def __init__(self, client : CxOneClient):
    self.__lock = asyncio.Lock()
    self.__data = None
    self.__index = {}
    self.__dirty = []
    self.__delete = []
    self.__client = client

  @property
  def client(self) -> CxOneClient:
    """The client used with this instance of the class."""
    return self.__client

  async def _load_config(self) -> List[Dict]:
    raise NotImplementedError("_load_config")

  async def _write_config(self, items : List[Dict]) -> None:
    raise NotImplementedError("_write_config")

  async def _write_deletes(self, keys : List[str]) -> None:
    raise NotImplementedError("_write_deletes")

  async def commit_config(self) -> None:
    """Writes scan configuration changes at the scope of the class implementation."""
    async with self.__lock:
      if len(self.__delete) > 0:
        await self._write_deletes([self.__data[i]['key'] for i in self.__delete])
        self.__delete = []

      if len(self.__dirty) > 0:
        await self._write_config([self.__data[i] for i in self.__dirty])
        self.__dirty = []

    await self.__populate(True)
  
  async def __populate(self, force : bool = False):
    async with self.__lock:
      if self.__data is None or force:
        self.__data = await self._load_config()
        self.__index = {}
        for i in range(0, len(self.__data)):
          self.__index[self.__data[i]['key']] = i

  async def __set_element(self, index : int, key : str, value : Any) -> None:
    async with self.__lock:
      self.__data[index][key] = value
      if index not in self.__dirty:
        self.__dirty.append(index)

  async def __get_element(self, index : int, key : str) -> Any:
    async with self.__lock:
      return self.__data[index][key]

  async def _set_value(self, key : str, value : Any) -> None:
    await self.__populate()
    if key in self.__index.keys():
      await self.__set_element(self.__index[key], 'value', value)

  async def _set_override(self, key : str, value : Any) -> None:
    await self.__populate()
    if key in self.__index.keys():
      await self.__set_element(self.__index[key], 'allowOverride', value)

  async def _get_value(self, key : str) -> Any:
    await self.__populate()
    if key not in self.__index.keys():
      return None
    else:
      return await self.__get_element(self.__index[key], 'value')

  async def _get_override(self, key : str) -> Any:
    await self.__populate()
    if key not in self.__index.keys():
      return None
    else:
      return await self.__get_element(self.__index[key], 'allowOverride')

  async def _delete_config(self, key : str) -> None:
    await self.__populate()
    async with self.__lock:
      if key in self.__index.keys():
        self.__delete.append(self.__index[key])

from typing import List, Any
from ...client import CxOneClient
from ...util import page_generator
from ...low.access_mgmt.user_mgmt import retrieve_groups
from ...low.projects import retrieve_list_of_projects
import asyncio
from dataclasses import dataclass
from pathlib import PosixPath


@dataclass(frozen=True)
class GroupDescriptor:
  id : str
  path : PosixPath
  name : str
  parent : Any = None
  roles : Any = None


class Groups:
  def __init__(self, client : CxOneClient):
    self.__client = client
    self.__lock = asyncio.Lock()
    self.__indexed = False
    self.__by_gid = {}
    self.__by_path = {}

  def __GroupDescriptor_factory(self, json : dict) -> GroupDescriptor:
    if json is None:
      return None
    
    if json['parentID'] is not None and len(json['parentID']) > 0 and json['parentID'] in self.__by_gid.keys():
      parent = self.__GroupDescriptor_factory(self.__by_gid[json['parentID']])
    else:
      parent = None

    return GroupDescriptor(json['id'], "/" / PosixPath(json['name']), json['briefName'], parent, json['roles'])

  async def __populate_indexes(self):
    async with self.__lock:
      if not self.__indexed:
        self.__indexed = True
        async for g in page_generator(retrieve_groups, client=self.__client):
          self.__by_gid[g['id']] = g
          self.__by_path[str("/" / PosixPath(g['name']))] = g

  async def get_path_list(self) -> List[str]:
    await self.__populate_indexes()
    return list(self.__by_path.keys())

  async def get_by_id(self, group_id : str) -> GroupDescriptor:
    await self.__populate_indexes()

    if group_id not in self.__by_gid.keys():
      return None

    return self.__GroupDescriptor_factory(self.__by_gid[group_id])

  async def get_by_full_path(self, path : str) -> GroupDescriptor:
    await self.__populate_indexes()

    if path not in self.__by_path.keys():
      return None

    return self.__GroupDescriptor_factory(self.__by_path[path])

  async def get_by_name(self, name : str) -> List[GroupDescriptor]:
    await self.__populate_indexes()
    return [self.__GroupDescriptor_factory(self.__by_path[x]) for x in self.__by_path.keys() if name in x]

  async def get_project_ids_by_groups(self, groups : List[GroupDescriptor]) -> List[str]:
    found = []
    async for p in page_generator(retrieve_list_of_projects, "projects", client=self.__client, 
      groups="|".join([g.id for g in groups])):
      found.append(p['id'])
    
    return found
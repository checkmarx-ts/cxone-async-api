from typing import List, Any, Union
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
    """A class used for reading IAM groups from Checkmarx One
    
      :param client: The CxOneClient instance used to communicate with Checkmarx One
      :type client: CxOneClient
    
    """
    self.__client = client
    self.__lock = asyncio.Lock()
    self.__indexed = False
    self.__by_gid = {}
    self.__by_path = {}

  def __GroupDescriptor_factory(self, json : dict) -> GroupDescriptor:
    if json is None:
      return None
    
    if json.get('parentID') is not None and len(json['parentID']) > 0 and json['parentID'] in self.__by_gid.keys():
      parent = self.__GroupDescriptor_factory(self.__by_gid[json['parentID']])
    else:
      parent = None

    return GroupDescriptor(json['id'], "/" / PosixPath(json['name']), json.get('briefName'), parent, json.get('roles'))

  async def __populate_indexes(self):
    async with self.__lock:
      if not self.__indexed:
        self.__indexed = True
        async for g in page_generator(retrieve_groups, client=self.__client):
          self.__by_gid[g['id']] = g
          self.__by_path[str("/" / PosixPath(g['name']))] = g

  async def get_path_list(self) -> List[str]:
    """Returns a list of group paths.
        
    :rtype: List[str]
    """
    await self.__populate_indexes()
    return list(self.__by_path.keys())

  async def get_by_id(self, group_id : str) -> GroupDescriptor:
    """Retrieve a GroupDescriptor by group ID.
    
    :param group_id: The ID of the group descriptor to retrieve.
    :type group_id: str

    :rtype: GroupDescriptor
    """
    await self.__populate_indexes()

    if group_id not in self.__by_gid.keys():
      return None

    return self.__GroupDescriptor_factory(self.__by_gid[group_id])

  async def get_by_full_path(self, path : str) -> Union[None, GroupDescriptor]:
    """Retrieve a GroupDescriptor by the full path of the group.

      Returns None if the path does not match a known group.
    
      :param path: The full group path.
      :type path: str
    
      :rtype: Union[None, GroupDescriptor]
    """
    await self.__populate_indexes()

    if path not in self.__by_path.keys():
      return None

    return self.__GroupDescriptor_factory(self.__by_path[path])

  async def get_by_name(self, name : str) -> List[GroupDescriptor]:
    """Retrieve a list of GroupDescriptors that match a group name.
    
      :param name: The name of the group, usually the last segment in a full group path.
      :type name: str
    
      :rtype: List[GroupDescriptor]
    """
    await self.__populate_indexes()
    return [self.__GroupDescriptor_factory(self.__by_path[x]) for x in self.__by_path.keys() if name in x]

  async def get_project_ids_by_groups(self, groups : List[GroupDescriptor]) -> List[str]:
    """Retrieves a list of project IDs of projects assigned to any of a list of provided groups.
    
      :param groups: A list of GroupDescriptors of groups that will filter the returned project IDs.
      :type groups: List[GroupDescriptor]

      :returns: A list of project IDs assigned to any of the given groups.  The list is empty if no projects have been assigned to any of the groups.
      :rtype: List[str]

    """
    found = []
    async for p in page_generator(retrieve_list_of_projects, "projects", client=self.__client, 
      groups="|".join([g.id for g in groups])):
      found.append(p['id'])
    
    return found
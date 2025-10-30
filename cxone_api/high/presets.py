import asyncio
import enum
from typing import List, Dict, AsyncGenerator, Union
from dataclasses import dataclass
from cxone_api import CxOneClient
from cxone_api.low.preset_management.presets import retrieve_list_of_presets, retrieve_list_of_queries_in_a_preset
from cxone_api.low.preset_management.queries import retrieve_list_of_queries_in_a_family, retrieve_list_of_query_families
from cxone_api.util import json_on_ok


class PresetEngine(enum.Enum):
  SAST = "sast"
  IAC = "iac"

@dataclass(frozen=True)
class QueryDescriptor:
  ID : str
  Name : str
  TypeKey : str
  CategoryName : str
  CWE: int
  DescriptionId : Union[int, None]
  DescriptionUrl : Union[str, None]
  Severity : str
  Custom : bool


@dataclass(frozen=True)
class PresetQueryFamilyDescriptor:
  Name : str
  Queries : List[QueryDescriptor]


@dataclass(frozen=True)
class PresetDescriptor:
  ID : str
  Engine : PresetEngine
  Name : str
  Description : str
  Custom : bool
  QueryFamilies : List[PresetQueryFamilyDescriptor]
  

class NameNotFoundException(Exception):
  @property
  def name(self) -> str:
    return self.__name
  
  def __init__(self, name : str):
    super().__init__(f"Unknown: {name}")
    self.__name = name


class PresetReader:
  def __init__(self, client : CxOneClient, engine : PresetEngine):
    self.__client = client
    self.__engine = engine
    self.__general_lock = asyncio.Lock()
    self.__family_lock = asyncio.Lock()
    self.__tenant_lock = asyncio.Lock()

    self.__notloaded_preset_ids = []
    self.__preset_name_index = {}
    self.__preset_id_index = {}
    
    self.__custom_preset_descriptors = []
    self.__standard_preset_descriptors = []

    self.__family_list = []
    self.__family_query_descriptor_index = {}
    self.__family_standard_query_descriptor_lists = {}
    self.__family_custom_query_descriptor_lists = {}

    self.__tenant_default_descriptor = None

  async def __preset_list_generator(self) -> AsyncGenerator:
    # The paging for the preset API is broken as of the writing of this code.  This is
    # a workaround until page_generator can be used.
    offset = 0
    page = None
    cur_page_index = 0
    while True:
      # pylint: disable=E1136
      if page is None or cur_page_index == page['totalFilteredCount']:
        page = json_on_ok(await retrieve_list_of_presets(self.__client, self.__engine.value, offset=offset, limit=100))
        cur_page_index = 0
        max = page['totalCount']

      if offset < max:
        offset += 1
        yield page['presets'][cur_page_index]
        cur_page_index += 1

      if offset == max:
        break

  async def __preload(self):
    # This does a preload of the presets for indexing purposes.
    # Detailed information for the presets is lazy loaded.
    async with self.__general_lock:
      if len(self.__notloaded_preset_ids) == 0 and len(self.__preset_name_index) == 0:
        async for preset_data in self.__preset_list_generator():
          self.__notloaded_preset_ids.append(preset_data['id'])
          self.__preset_name_index[preset_data['name']] = preset_data['id']

  async def __populate_family_query_descriptor_cache(self, family_name : str) -> None:
    if not family_name in await self.get_query_families():
      raise NameNotFoundException(family_name)
    
    async with self.__family_lock:
      if family_name not in self.__family_query_descriptor_index.keys():
        # Cache the query descriptors for the family the first time the family
        # is requested.
        self.__family_query_descriptor_index[family_name] = {}
        self.__family_standard_query_descriptor_lists[family_name] = []
        self.__family_custom_query_descriptor_lists[family_name] = []

        family_queries = json_on_ok(await retrieve_list_of_queries_in_a_family(self.__client, self.__engine.value, family_name))

        for query_type in family_queries:
          TypeKey = query_type['key']
          for query_category in query_type['children']:
            CategoryName = query_category['title']
            for query_detail in query_category['children']:
              qid = query_detail['key']
              descriptor = \
                QueryDescriptor(ID=qid, 
                                Name=query_detail['title'],
                                TypeKey=TypeKey,
                                CategoryName=CategoryName,
                                CWE = query_detail['data']['cwe'],
                                Severity = query_detail['data']['severity'],
                                Custom = query_detail['data']['custom'],
                                DescriptionId = query_detail['data'].get('queryDescriptionId'),
                                DescriptionUrl = query_detail['data'].get('url')
                                )

              self.__family_query_descriptor_index[family_name][qid] = descriptor

              if descriptor.Custom:
                self.__family_custom_query_descriptor_lists[family_name].append(descriptor)
              else:
                self.__family_standard_query_descriptor_lists[family_name].append(descriptor)

  async def __create_family_descriptor(self, family_name : str, query_ids : List[str]) -> PresetQueryFamilyDescriptor:
      await self.__populate_family_query_descriptor_cache(family_name)
      return PresetQueryFamilyDescriptor(Name=family_name, 
                                         Queries = [self.__family_query_descriptor_index[family_name][qid] for qid in query_ids])

  async def __create_family_descriptors_from_json(self, family_dicts : List[Dict]) -> List[PresetQueryFamilyDescriptor]:
    return await asyncio.gather(*[self.__create_family_descriptor(f['familyName'], f['queryIds']) for f in family_dicts])

  async def __cache_unloaded_preset_no_lock(self, id : str) -> None:
    if id in self.__notloaded_preset_ids:
      # Populate the internal preset descriptor cache
      query_list = json_on_ok(await retrieve_list_of_queries_in_a_preset(self.__client, self.__engine.value, id))
      self.__preset_id_index[id] = \
        PresetDescriptor(ID = id, 
                          Engine=self.__engine, 
                          Name=query_list['name'],
                          Description=query_list['description'],
                          Custom=query_list['custom'],
                          QueryFamilies=await self.__create_family_descriptors_from_json(query_list['queries'])
                          )

      if query_list['isTenantDefault']:
        self.__tenant_default_descriptor = self.__preset_id_index[id]
      
      if query_list['custom']:
        self.__custom_preset_descriptors.append(self.__preset_id_index[id])
      else:
        self.__standard_preset_descriptors.append(self.__preset_id_index[id])

      self.__notloaded_preset_ids.remove(id)


  async def __get_preset(self, id : str) -> PresetDescriptor:
    async with self.__general_lock:
      await self.__cache_unloaded_preset_no_lock(id)
    return self.__preset_id_index[id]
  
  async def get_tenant_default_preset(self) -> Union[PresetDescriptor, None]:
    await self.__preload()

    async with self.__tenant_lock:
      if self.__tenant_default_descriptor is None:
        async with self.__general_lock:
          ids_copy = self.__notloaded_preset_ids.copy()
          for next_id in ids_copy:
            await self.__cache_unloaded_preset_no_lock(next_id)
            if self.__tenant_default_descriptor is not None:
              break

    return self.__tenant_default_descriptor

  async def get_preset_by_id(self, id : str) -> PresetDescriptor:
    await self.__preload()
    return await self.__get_preset(id)

  async def get_preset_by_name(self, name : str) -> PresetDescriptor:
    await self.__preload()
    if name in self.__preset_name_index.keys():
      return await self.__get_preset(self.__preset_name_index[name])
    else:
      raise NameNotFoundException(name)
  
  async def __cache_all_presets(self) -> None:
    await self.__preload()
    async with self.__general_lock:
      ids_copy = self.__notloaded_preset_ids.copy()
      for next_id in ids_copy:
        await self.__cache_unloaded_preset_no_lock(next_id)

  async def get_presets(self) -> List[PresetDescriptor]:
    await self.__cache_all_presets()
    return self.__custom_preset_descriptors + self.__standard_preset_descriptors
  
  async def get_custom_presets(self) -> List[PresetDescriptor]:
    await self.__cache_all_presets()
    return self.__custom_preset_descriptors

  async def get_standard_presets(self) -> List[PresetDescriptor]:
    await self.__cache_all_presets()
    return self.__standard_preset_descriptors
    
  async def get_queries_by_family(self, family_name : str) -> List[QueryDescriptor]:
    await self.__preload()
    await self.__populate_family_query_descriptor_cache(family_name)
    return self.__family_standard_query_descriptor_lists[family_name] + \
      self. __family_custom_query_descriptor_lists[family_name]

  async def get_standard_queries_by_family(self, family_name : str) -> List[QueryDescriptor]:
    await self.__preload()
    await self.__populate_family_query_descriptor_cache(family_name)
    return self.__family_standard_query_descriptor_lists[family_name]

  async def get_custom_queries_by_family(self, family_name : str) -> List[QueryDescriptor]:
    await self.__preload()
    await self.__populate_family_query_descriptor_cache(family_name)
    return self.__family_custom_query_descriptor_lists[family_name]
  
  async def get_query_families(self) -> List[str]:
    async with self.__family_lock:
      if len(self.__family_list) == 0:
        self.__family_list = json_on_ok(await retrieve_list_of_query_families(self.__client, self.__engine.value))
    return self.__family_list

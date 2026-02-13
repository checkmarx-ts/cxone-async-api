from cxone_api import CxOneClient
from cxone_api.util import json_on_ok
from typing import Dict, List
import asyncio
from requests import post


class abstract_iterator:

  def __init__(self, client : CxOneClient, api_url : str, query : str, element_name : str, page_size : int, page_retries_max : int = 5, page_retry_delay_s : int = 3):
    self.__client = client
    self.__url = api_url
    self.__query = query
    self.__elem = element_name
    self.__page_size = page_size
    self.__next_skip = 0
    self.__max = 0
    self.__retry = page_retries_max
    self.__retry_delay = page_retry_delay_s
    self.__cache = None

  def _add_variables(self, to_dict : Dict) -> None:
    raise NotImplementedError("_add_variables")

  async def __anext__(self):
    retries = self.__retry
    if self.__cache is not None and len(self.__cache) == 0:

      if self.__next_skip < self.__max:
        raise StopAsyncIteration

    if self.__cache is None or len(self.__cache) == 0:
      while retries > 0:
        try:
          variables = {
                  "take": self.__page_size, 
                  "skip": self.__next_skip, 
          }
          self._add_variables(variables)

          payload = {
            "query" : self.__query,
            "variables" : variables
          }
          
          resp_json = json_on_ok(await self.__client.exec_request(post,
                                                          url=self.__url,
                                                          json=payload))

          data = resp_json.get("data", None)
          assert(data is not None)
          self.__cache = data.get(self.__elem, None)
          assert(self.__cache is not None)
        except BaseException:
          if retries > 0:
              await asyncio.sleep(self.__retry_delay)
              retries -= 1
              if retries == 0:
                raise
              continue

        if len(self.__cache) == 0:
          raise StopAsyncIteration

        break

      self.__max += self.__page_size

    self.__next_skip += 1
    return self.__cache.pop(0)


class where_iterator(abstract_iterator):
  def __init__(self, where_dict : Dict, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.__where = where_dict

  def _add_variables(self, to_dict : Dict) -> None:
    to_dict['where'] = self.__where


class ordered_iterator(where_iterator):
  def __init__(self, order_list : List[Dict], *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.__order = order_list

  def _add_variables(self, to_dict : Dict) -> None:
    super()._add_variables(to_dict)
    to_dict['order'] = self.__order

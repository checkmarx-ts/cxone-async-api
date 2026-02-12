from cxone_api import CxOneClient
from cxone_api.util import json_on_ok
from typing import Dict, List, Union
from requests.compat import urljoin
from requests import post
import asyncio

class ResultOrder:
  def __init__(self):
    self.__ascending = []
    self.__descending = []

  def add_ascending(self, field_name : str) -> None:
    self.__ascending.append(field_name)

  def add_descending(self, field_name : str) -> None:
    self.__descending.append(field_name)

  def render(self) -> Dict:
    order = [{asc : "ASC"} for asc in self.__ascending] + [{desc : "DESC"} for desc in self.__descending]
    return order if len(order) > 0 else None


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



class AbstractScaGQLQuery:
  def __init__(self, client : CxOneClient, page_size : int = 500, page_retries_max : int = 5, page_retry_delay_s : int = 3):
    self.__client = client
    self.__page_size = page_size
    self.__retries = page_retries_max
    self.__retry_delay = page_retry_delay_s

  def __aiter__(self):
    raise NotImplementedError("__aiter__")

  @property
  def _retries(self) -> int:
    return self.__retries

  @property
  def _retry_delay(self) -> int:
    return self.__retry_delay
  
  @property
  def _client(self) -> CxOneClient:
    return self.__client
  
  @property
  def _page_size(self) -> int:
    return self.__page_size

  @property
  def _gql_endpoint_url(self) -> str:
    return urljoin(self.__client.api_endpoint, "/api/sca/graphql/graphql")
  
  @property
  def _query(self) -> str:
    raise NotImplementedError("query")

  @property
  def _result_element(self) -> str:
    raise NotImplementedError("result_element")
  

class AbstractScaGQLWhereQuery(AbstractScaGQLQuery):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.__where = None

  @property
  def where(self) -> Dict:
    return self.__where

  @where.setter
  def where(self, where_tree : Dict) -> None:
    self.__where = where_tree

  def __aiter__(self):
    return where_iterator(self.__where, 
                          client=self._client, 
                          api_url=self._gql_endpoint_url, 
                          query=self._query, 
                          element_name=self._result_element,
                          page_size=self._page_size,
                          page_retries_max=self._retries,
                          page_retry_delay_s=self._retry_delay)


class AbstractScaGQLOrderQuery(AbstractScaGQLWhereQuery):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.__order = ResultOrder()

  @property
  def order(self) -> ResultOrder:
    return self.__order

  def __aiter__(self):
    return ordered_iterator(self.order.render(), self.where, 
                          client=self._client, 
                          api_url=self._gql_endpoint_url, 
                          query=self._query, 
                          element_name=self._result_element,
                          page_size=self._page_size,
                          page_retries_max=self._retries,
                          page_retry_delay_s=self._retry_delay)

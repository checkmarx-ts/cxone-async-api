from cxone_api import CxOneClient
from cxone_api.util import json_on_ok
from typing import Dict
from requests.compat import urljoin
from .iterators import where_iterator, ordered_iterator

class ResultOrder:
  """A class used to build GraphQL ordering directives."""
  def __init__(self):
    self.__ascending = []
    self.__descending = []

  def add_ascending(self, field_name : str) -> None:
    """Adds a field name to sort in ascending order.
    
    :param field_name: The name of the field to be sorted.
    :type field_name: str
    """
    self.__ascending.append(field_name)

  def add_descending(self, field_name : str) -> None:
    """Adds a field name to sort in descending order.
    
    :param field_name: The name of the field to be sorted.
    :type field_name: str
    """
    self.__descending.append(field_name)

  def render(self) -> List[Dict]:
    """Renders the GraphQL order structure.
    
    :return: Returns a list of dictionaries containing the sort order instructions.
    :rtype: List[Dict]
    """
    order = [{asc : "ASC"} for asc in self.__ascending] + [{desc : "DESC"} for desc in self.__descending]
    return order if len(order) > 0 else None





class AbstractScaGQLQuery:
  """The abstract implementation for an SCA analysis query using GraphQL."""

  def __init__(self, client : CxOneClient, page_size : int = 500, page_retries_max : int = 5, page_retry_delay_s : int = 3):
    """GraphQL query class instances function as asynchronous iterators.
    
    :param client: The CxOneClient instance used to communicate with Checkmarx One
    :type client: CxOneClient
    
    :param page_size: The maximum number of results to retrieve with each API call, defaults to 500.
    :type page_size: int

    :param page_retries_max: The number of retries to attempt if there is an error when retrieving a page of data from the API, defaults to 5.
    :type page_retries_max: int

    :param page_retry_delay_s: The number of seconds to wait between each retry attempt, defaults to 3.
    :type page_retry_delay_s: int
    """
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
  """An SCA analysis GraphQL query that supports results filtering."""

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.__where = None

  @property
  def where(self) -> Dict:
    """Returns the dictionary that defines the query filtering criteria.
    
    :return: A dictionary containing the query filtering criteria.
    :rtype: Dict
    """
    return self.__where

  @where.setter
  def where(self, where_tree : Dict) -> None:
    """A property that is set to a dictionary containing the query filtering criteria.
    
    :param where_tree: A dictionary representing a boolean statement in the form of a logical tree.
    :type where_tree: Dict
    """
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
  """An SCA analysis GraphQL query that supports both results filtering and ordering."""
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.__order = ResultOrder()

  @property
  def order(self) -> ResultOrder:
    """Returns the object where fields can be set for result ordering.
    
    :rtype: ResultOrder
    """
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

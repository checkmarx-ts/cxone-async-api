import re, urllib, requests, logging, functools, inspect, asyncio
from datetime import datetime
from requests import Response
from requests.compat import urljoin
from .exceptions import ResponseException
from .client import CxOneClient
from typing import Coroutine, List

def json_on_ok(response : Response, specific_responses : List[int] = None):
    """A utility function that retrieves the json from a requests.Response object. 
    
    If response.ok is true, a JSON dictionary is returned. If response.ok is false, ResponseException is thrown.

    :param response: A `requests.Response` object with content that is JSON.
    :type response: requests.Response

    :param specific_responses: A list of integers indicating HTTP status codes
                               that indicate the response is value.
                               Defaults to None.
    :type specific_responses: List[int], optional

    :raises ResponseException: Exception is raised when response.ok is false or
                               the value for `response.status_code` is not
                               a member of the list of responses given in
                               `specific_responses`.

    :return: A JSON dictionary obtained from the response.
    :rtype: Dict
    """
    if (specific_responses is None and response.ok) or \
        (specific_responses is not None and response.status_code in specific_responses):
        return response.json()
    else:
        raise ResponseException(f"Unable to get JSON response: Code: "
            f"[{response.status_code}] Url: {response.request.url}")

class CloneUrlParser:
    """A parser for obtaining organization and repository name elements from a Git clone URL.
    
    The primary use is to normalize retrieval of the organization and repository elements when the Git server
    implementation adds additional components that are irrelevant for many cases.

    :param repo_type: The name of the repository type.  A value other than `azure` or `bitbucket` parses the `clone_url` value
                        to assume the path is "<organization>/<repository name>"
    :type repo_type: str

    :param clone_url: A Git clone url.
    :type clone_url: str

    :rtype: CloneUrlParser
    """

    __parsers = {
        "bitbucket" : re.compile("^(?P<scheme>.+)://((?P<cred>.+)@)?.+/(scm/)?(?P<org>.+)/(?P<repo>.+?)(\\.git)?$"),
        "azure" : re.compile("^(?P<scheme>.+)://((?P<cred>.+)@)?.+/(?P<org>.+)/(?P<project>.+)/_git/(?P<repo>.+?)(\\.git)?$")
    }

    __default = re.compile("^.*[/:]{1}(?P<org>.+)/(?P<repo>.+?)(\\.git)?$")

    def __init__(self, repo_type, clone_url):
        matcher = CloneUrlParser.__parsers[repo_type] \
            if repo_type in CloneUrlParser.__parsers.keys() else CloneUrlParser.__default
        computed_match = matcher.match(clone_url)
        self.__the_match = computed_match.groupdict() if computed_match is not None else {}

    def __get_prop_or_none(self, name):
        return  self.__the_match[name] if name in self.__the_match.keys() else None

    @property
    def scheme(self) -> str:
        """The transport scheme (e.g. http)"""
        return self.__get_prop_or_none("scheme")

    @property
    def creds(self) -> str:
        """The `username:password` credentials, if any."""
        return self.__get_prop_or_none("cred")

    @property
    def org(self) -> str:
        """The name of the organization owning the repository."""
        return self.__get_prop_or_none("org")

    @property
    def repo(self) -> str:
        """The name of the repository."""
        return self.__get_prop_or_none("repo")


def dashargs(*args : str):
    """A utility decorator to translate python kwargs when an API's parameter has a dash in the name.
    
    This converts API parameters to their proper name when the API defines them with "-"
    in the parameter name.  This allows API methods to use kwargs with names defined in the API
    rather than mapping argument names to API query parameters.

    This decorator will attempt to match key names in kwargs parameters
    passed in the form.  For example, for API parameter "param-name",
    the decorator would be:

    @dashargs("param-name")

    And the kwarg name match would match on either of the following key words:

    * param_name
    * paramname


    :param args: A comma-separated list of strings that match a dashed API argument (e.g. "foo-bar" but not "foobar")
    :type args: *str

    :return: A Callable that wraps the decorated function.
    :rtype: Callable
    """

    def normalized_string(s):
        return s.replace('-', '').replace('_', '')


    def decorator(wrapped):

        @functools.wraps(wrapped)
        async def wrapper(*inner_args, **inner_kwargs):

            normalized = {}

            for val in args:
                normalized[normalized_string(val)] = val


            to_delete = []
            to_add = {}

            for k in inner_kwargs:

                nk = normalized_string(k)

                if nk in normalized.keys():
                    to_add[normalized[nk]] = inner_kwargs[k]
                    to_delete.append(k)

            inner_kwargs = inner_kwargs | to_add

            for k in to_delete:
                del inner_kwargs[k]

            return await wrapped(*inner_args, **inner_kwargs)
        return wrapper
    return decorator



async def page_generator(coro : Coroutine, array_element : str = None, offset_param : str = 'offset', offset_init_value : int = 0, 
                         offset_is_by_count : bool = True, page_retries_max : int = 5, page_retry_delay_s : int = 3, 
                         key_element_name : str = None, **kwargs):
    """An async generator function that is used to automatically fetch the next page of results from the API.
     
    This is used for a variety of APIs where the full result set is too large to return as a single payload.  The API
    will support a way to retrieve a "page" of results by adjusting parameters sent with subsequent calls.

    :param coro: The coroutine executed to fetch data from the API, usually a method from the low module.
    :type coro: Coroutine
    
    :param array_element: The root element in the JSON response containing the array of results. Use None if the root element is the array element. Defaults to None.
    :type array_element: str, optional

    :param offset_param: The name of the API parameter that dictates the page offset of the values to fetch. Defaults to 'offset'.
    :type offset_param: str, optional


    :param offset_init_value: The initial value set in the offset parameter. Defaults to 0.
    :type offset_init_value: int, optional

    :param offset_is_by_count: Set to true if the API next offset is indicated by count of elements retrieved.
                               If set to false, the offset is incremented by one to indicate a page offset where the count
                               of results per page is set by other parameters. Defaults to true.
    :type offset_is_by_count: bool, optional


    :param page_retries_max: The number of retries to fetch a page in the event of an error.  Defaults to 5.
    :type page_retries_max: int, optional

    :param page_retry_delay_s: The number of seconds to delay the next page fetch retry.  Defaults to 3 seconds.
    :type page_retry_delay_s: int, optional

    :param key_element_name: If the API response is a dictionary, the results are values assigned to each key element.  If
                        this parameter is included, the key element with this name is added to the returned data. Defaults to None.
    :type key_element_name: str, optional

    
    :param kwargs: Keyword args passed to the coroutine at the time the coroutine is executed.

    :raises BaseException: Exceptions thrown by the coroutine are raised after retries.

    :return: A generator that is used in an `async for` statement.
    :rtype: Generator
"""
    _log = logging.getLogger(f"page_generator:{inspect.unwrap(coro).__name__}")

    offset = offset_init_value
    buf = []
    retries = 0


    while True:
        if len(buf) == 0:
            try:
                kwargs[offset_param] = offset
                json = (await coro(**kwargs)).json()
                buf = json[array_element] if array_element is not None else json
                if isinstance(buf, dict):
                    if key_element_name is None:
                        buf = [buf[k] for k in buf.keys()]
                    else:
                        buf = [{key_element_name : k} | buf[k] for k in buf.keys()]

                retries = 0

                if buf is None or len(buf) == 0:
                    return

                if offset_is_by_count:
                    offset = offset + len(buf)
                else:
                    offset += 1
            except BaseException as ex:
                if retries < page_retries_max:
                    _log.debug(f"Exception fetching next page, will retry: {ex}")
                    await asyncio.sleep(page_retry_delay_s)
                    retries += 1
                    continue
                else:
                    _log.debug(f"Abort after {retries} retries", ex)
                    raise

        yield buf.pop(0)


def join_query_dict(url, querydict) -> str:
    """A utility function for appending a query string to a URL following Checkmarx One conventions.
    
    All string key/value pairs or strings in a list are urlencoded.
    Non-string object types are converted to string and should perform their own
    urlencoding as needed.

    :param url: A URL string to which the query string will be appended.
    :type url: str

    :param querydict: A dictionary of key/value pairs used to build the query string.
    :type querydict: Dict

    :return: The value of `url` with a query string appended.
    :rtype: str
    """
    query = []
    for key in querydict.keys():
        if querydict[key] is None:
            continue

        if isinstance(querydict[key], list):
            query.append(f"{urllib.parse.quote(key)}="
                f"{urllib.parse.quote(','.join(querydict[key]))}")
        elif isinstance(querydict[key], str):
            query.append(f"{urllib.parse.quote(key)}={urllib.parse.quote(querydict[key])}")
        else:
            query.append(f"{urllib.parse.quote(key)}={querydict[key]}")


    return urljoin(url, f"?{'&'.join(query)}" if len(query) > 0 else '')


import re
import urllib
from datetime import datetime
from requests import Response
from requests.compat import urljoin
from .exceptions import ResponseException
from .client import CxOneClient

def json_on_ok(response : Response, specific_responses : list = None):
    """
    A utility function that retrieves the json from a requests.Response object if the
    response.ok is true.  If response.ok is false, ResponseException is thrown.
    """
    if (specific_responses is None and response.ok) or \
        (specific_responses is not None and response.status_code in specific_responses):
        return response.json()
    else:
        raise ResponseException(f"Unable to get JSON response: Code: "
            f"[{response.status_code}] Url: {response.request.url}")

class CloneUrlParser:
    """
    A parser for obtaining configuration elements from a clone URL
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
        return self.__get_prop_or_none("scheme")

    @property
    def creds(self) -> str:
        return self.__get_prop_or_none("cred")

    @property
    def org(self) -> str:
        return self.__get_prop_or_none("org")

    @property
    def repo(self) -> str:
        return self.__get_prop_or_none("repo")


def dashargs(*args : str):
    """A utility decorator to convert kwargs used for API calls
    to their proper name when the API defines them with "-"
    in the argument name.  This allows API methods to use kwargs
    with names defined in the API rather than mapping argument names
    to API query parameters.

    This decorator will attempt to match key names in kwargs parameters
    passed in the form.  For example, for API parameter "param-name",
    the decorator would be:

    @dashargs("param-name")

    And the kwarg name match would match on either of the following key words:

    * param_name
    * paramname


    Parameters:
        args - Strings that match a dashed API argument (e.g. "foo-bar" but not "foobar")
    """

    def normalized_string(s):
        return s.replace('-', '').replace('_', '')


    def decorator(wrapped):
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



async def page_generator(coro, array_element, offset_param='offset', **kwargs):
    """
    An async generator function that is used to automatically fetch the next page
    of results from the API when the API supports result paging.

    Parameters:
        coro - The coroutine executed to fetch data from the API.
        array_element - The root element in the JSON response containing the array of results.
        offset_param - The name of the API parameter that dictates the page offset 
        of the values to fetch.
        kwargs - Keyword args passed to the coroutine at the time the coroutine is executed.
    """
    offset = 0
    buf = []

    while True:
        if len(buf) == 0:
            kwargs[offset_param] = offset
            buf = (await coro(**kwargs)).json()[array_element]

            if buf is None or len(buf) == 0:
                return

            offset = offset + len(buf)

        yield buf.pop()


def join_query_dict(url, querydict):
    query = []
    for key in querydict.keys():
        if querydict[key] is None:
            continue

        if isinstance(querydict[key], list):
            query.append(f"{urllib.parse.quote(key)}="
                f"{urllib.parse.quote(','.join(querydict[key]))}")
        elif isinstance(querydict[key], str):
            query.append(f"{urllib.parse.quote(key)}={urllib.parse.quote(querydict[key])}")
        elif isinstance(querydict[key], type(datetime)):
            pass # TODO: datetime as ISO 8601 string
        else:
            query.append(f"{urllib.parse.quote(key)}={querydict[key]}")


    return urljoin(url, f"?{'&'.join(query)}" if len(query) > 0 else '')

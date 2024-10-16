"""Module that implements the CxOneClient object"""
import asyncio
import uuid
import urllib
import requests
from .__version__ import __version__ as cxone_api_version
from .exceptions import AuthException, CommunicationException


class CxOneClient:
    __AGENT_NAME = 'CxOne PyClient'

    def __common__init(self, agent_name, tenant_auth_endpoint,
        api_endpoint, timeout, retries, proxy, ssl_verify):

        self.__version = cxone_api_version
        self.__agent = f"{agent_name}/({CxOneClient.__AGENT_NAME}/{self.__version})"
        self.__proxy = proxy
        self.__ssl_verify = ssl_verify
        self.__auth_lock = asyncio.Lock()
        self.__corelation_id = str(uuid.uuid4())

        self.__auth_endpoint = tenant_auth_endpoint
        self.__api_endpoint = api_endpoint
        self.__timeout = timeout
        self.__retries = retries

        self.__auth_result = None


    @staticmethod
    def create_with_oauth(oauth_id, oauth_secret, agent_name, tenant_auth_endpoint,
                          api_endpoint, timeout=60, retries=3, proxy=None, ssl_verify=True):
        inst = CxOneClient()
        inst.__common__init(agent_name, tenant_auth_endpoint, api_endpoint, timeout,
                            retries, proxy, ssl_verify)

        inst.__auth_content = urllib.parse.urlencode( {
            "grant_type" : "client_credentials",
            "client_id" : oauth_id,
            "client_secret" : oauth_secret
        })

        return inst

    @staticmethod
    def create_with_api_key(api_key, agent_name, tenant_auth_endpoint,
        api_endpoint, timeout=60, retries=3, proxy=None, ssl_verify=True):
        inst = CxOneClient()
        inst.__common__init(agent_name, tenant_auth_endpoint,
                            api_endpoint, timeout, retries, proxy, ssl_verify)

        inst.__auth_content = urllib.parse.urlencode( {
            "grant_type" : "refresh_token",
            "client_id" : "ast-app",
            "refresh_token" : api_key
        })

        return inst

    @property
    def auth_endpoint(self):
        return str(self.__auth_endpoint)

    @property
    def api_endpoint(self):
        return str(self.__api_endpoint)

    @property
    def display_endpoint(self):
        return str(self.__api_endpoint.display_endpoint)

    @property
    def admin_endpoint(self):
        return self.__auth_endpoint.admin_endpoint

    async def __get_request_headers(self):
        if self.__auth_result is None:
            await self.__do_auth()

        return {
            "Authorization" : f"Bearer {self.__auth_result['access_token']}",
            "Accept" : "*/*; version=1.0", 
            "User-Agent" : self.__agent,
            "CorrelationId" : self.__corelation_id
            }

    async def __auth_task(self):
        response = None
        for _ in range(0, self.__retries):
            response = await asyncio.to_thread(requests.post, self.auth_endpoint,
              data=self.__auth_content, timeout=self.__timeout,
              proxies=self.__proxy, verify=self.__ssl_verify, headers={
                  "Content-Type" : "application/x-www-form-urlencoded",
                  "Accept" : "application/json"
              })
            if response.ok:
                return response.json()

        raise AuthException("CheckmarxOne response: "
                            f"{response.reason if not response is None else 'Unknown error'}")

    async def __do_auth(self):
        skip = False

        if self.__auth_lock.locked():
            skip = True
            async with self.__auth_lock:
                pass

        if not skip:
            async with self.__auth_lock:
                self.__auth_result = await self.__auth_task()

    async def exec_request(self, verb_func, *args, **kwargs):
        if not self.__proxy is None:
            kwargs['proxies'] = self.__proxy

        kwargs['verify'] = self.__ssl_verify

        for _ in range(0, self.__retries):
            auth_headers = await self.__get_request_headers()

            if 'headers' in kwargs.keys():
                for h in auth_headers.keys():
                    kwargs['headers'][h] = auth_headers[h]
            else:
                kwargs['headers'] = auth_headers

            response = await asyncio.to_thread(verb_func, *args, **kwargs)

            if response.status_code == 401:
                await self.__do_auth()
            else:
                return response

        raise CommunicationException(verb_func, *args, **kwargs)
    
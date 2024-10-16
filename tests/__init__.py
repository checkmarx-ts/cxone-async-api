import unittest
import os
import asyncio
from cxone_api import CxOneClient, AuthRegionEndpoints, ApiRegionEndpoints

class BaseTest(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        api_endpoint = ApiRegionEndpoints[os.environ['TEST_REGION']]()
        iam_endpoint = AuthRegionEndpoints[os.environ['TEST_REGION']](os.environ['TEST_TENANT_ID'])

        cls.client_oauth = CxOneClient.create_with_oauth(os.environ['TEST_OAUTH_CLIENT_ID'],
                                os.environ['TEST_OAUTH_CLIENT_SECRET'], "UnitTest",
                                iam_endpoint, api_endpoint)

        cls.client_apikey = CxOneClient.create_with_api_key(os.environ['TEST_API_KEY'],
                                "UnitTest", iam_endpoint, api_endpoint)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
   
    async def execute_client_call(self, coro, response_eval, kwarg_generators=None, *arg, **kwargs):

        def fill_kwargs():
            if kwarg_generators is not None:
                for k in kwarg_generators.keys():
                    kwargs[k] = kwarg_generators[k]()

        with self.subTest("apikey"):
            fill_kwargs()
            if asyncio.iscoroutinefunction(response_eval):
                await response_eval(await coro (self.client_apikey, *arg, **kwargs), self.client_apikey)
            else:
                response_eval(await coro(self.client_apikey, *arg, **kwargs), self.client_apikey)

        with self.subTest("oauth"):
            fill_kwargs()
            if asyncio.iscoroutinefunction(response_eval):
                await response_eval(await coro(self.client_oauth, *arg, **kwargs), self.client_oauth)
            else:
                response_eval(await coro(self.client_oauth, *arg, **kwargs), self.client_oauth)

    def assert_response_ok(self, response, client):
        self.assertTrue(response.ok)

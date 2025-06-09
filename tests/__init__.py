import unittest
import os
import asyncio
import time
from cxone_api.high.scans import ScanLoader
from cxone_api import CxOneClient, AuthRegionEndpoints, ApiRegionEndpoints
from dotenv import load_dotenv

class BaseTest(unittest.IsolatedAsyncioTestCase):
    DEFAULT_REPO = "https://github.com/nleach999/SimplyVulnerable.git"
    DEFAULT_BRANCH = "master"
    MAX_SCAN_SECONDS = 650

    @classmethod
    def setUpClass(cls):
        
        load_dotenv()

        api_endpoint = ApiRegionEndpoints[os.environ['TEST_REGION']]()
        iam_endpoint = AuthRegionEndpoints[os.environ['TEST_REGION']](os.environ['TEST_TENANT_ID'])

        cls.client_oauth = CxOneClient.create_with_oauth(os.environ['TEST_OAUTH_CLIENT_ID'],
                                os.environ['TEST_OAUTH_CLIENT_SECRET'], "UnitTest",
                                iam_endpoint, api_endpoint)

        cls.client_apikey = CxOneClient.create_with_api_key(os.environ['TEST_API_KEY'],
                                "UnitTest", iam_endpoint, api_endpoint)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    
    async def wait_for_scan_completion(self, client, scanid):
        start = time.time()
        while time.time() - start < BaseTest.MAX_SCAN_SECONDS:
            inspector = await ScanLoader.load(client, scanid)
            if inspector.executing:
                await asyncio.sleep(10.0)
                continue
            else:
                return inspector.successful
        
        return False
    

    async def execute_client_call(self, coro, response_eval, kwarg_generators=None, *arg, **kwargs):

        async def fill_kwargs():
            if kwarg_generators is not None:
                for k in kwarg_generators.keys():
                    kwargs[k] = kwarg_generators[k]() if not asyncio.iscoroutinefunction(kwarg_generators[k]) else \
                        await kwarg_generators[k]()

        async def apikey_task():
            with self.subTest("apikey"):
                await fill_kwargs()
                if asyncio.iscoroutinefunction(response_eval):
                    await response_eval(await coro (self.client_apikey, *arg, **kwargs), self.client_apikey)
                else:
                    response_eval(await coro(self.client_apikey, *arg, **kwargs), self.client_apikey)

        async def oauth_task():
            with self.subTest("oauth"):
                await fill_kwargs()
                if asyncio.iscoroutinefunction(response_eval):
                    await response_eval(await coro(self.client_oauth, *arg, **kwargs), self.client_oauth)
                else:
                    response_eval(await coro(self.client_oauth, *arg, **kwargs), self.client_oauth)

        await asyncio.gather(asyncio.create_task(oauth_task()), asyncio.create_task(apikey_task()))

    def assert_response_ok(self, response, client):
        if not response.ok:
            print(response.text)
        self.assertTrue(response.ok)

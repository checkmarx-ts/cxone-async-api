import unittest
import os
import asyncio, inspect
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

        proxy_url = os.environ.get("TEST_PROXY_URL")
        proxy = None
        ssl_verify = True
        if proxy_url is not None:
            proxy = {"HTTPS": proxy_url, "https": proxy_url}
            ssl_verify = False

        api_endpoint = ApiRegionEndpoints[os.environ["TEST_REGION"]]()
        iam_endpoint = AuthRegionEndpoints[os.environ["TEST_REGION"]](
            os.environ["TEST_TENANT_ID"]
        )

        cls.client_oauth = CxOneClient.create_with_oauth(
            os.environ["TEST_OAUTH_CLIENT_ID"],
            os.environ["TEST_OAUTH_CLIENT_SECRET"],
            "UnitTest",
            iam_endpoint,
            api_endpoint,
            ssl_verify=ssl_verify,
            proxy=proxy,
        )

        cls.client_apikey = CxOneClient.create_with_api_key(
            os.environ["TEST_API_KEY"],
            "UnitTest",
            iam_endpoint,
            api_endpoint,
            ssl_verify=ssl_verify,
            proxy=proxy,
        )

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

    async def execute_client_call(
        self, coro, response_eval, kwarg_generators=None, *arg, **kwargs
    ):

        async def fill_kwargs():
            if kwarg_generators is not None:
                for k in kwarg_generators.keys():
                    if not callable(kwarg_generators[k]):
                        kwargs[k] = kwarg_generators[k]
                    elif not inspect.iscoroutinefunction(kwarg_generators[k]):
                        kwargs[k] = kwarg_generators[k]()
                    else:
                        kwargs[k] = await kwarg_generators[k]()

        async def apikey_task():
            with self.subTest("apikey"):
                await fill_kwargs()
                response = None
                if inspect.iscoroutinefunction(response_eval):
                    response = await coro(self.client_apikey, *arg, **kwargs)
                    await response_eval(
                        response,
                        self.client_apikey,
                    )
                else:
                    response = await coro(self.client_apikey, *arg, **kwargs)
                    response_eval(
                        response,
                        self.client_apikey,
                    )
                return response

        async def oauth_task():
            with self.subTest("oauth"):
                await fill_kwargs()
                response = None
                if inspect.iscoroutinefunction(response_eval):
                    response = await coro(self.client_oauth, *arg, **kwargs)
                    await response_eval(response, self.client_oauth)
                else:
                    response = await coro(self.client_oauth, *arg, **kwargs)
                    response_eval(response, self.client_oauth)

                return response

        return await asyncio.gather(
            asyncio.create_task(oauth_task()), asyncio.create_task(apikey_task())
        )

    def assert_response_ok(self, response, client):
        if not response.ok:
            print(response.text)
        self.assertTrue(response.ok)

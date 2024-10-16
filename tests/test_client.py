import unittest
from cxone_api import CxOneClient, CxOneAuthEndpoint, CxOneApiEndpoint
from cxone_api.exceptions import EndpointException
from tests import BaseTest

class TestClient(BaseTest):
    
    async def test_canary(self):
        self.assertTrue(1 == 1)

    async def test_auth_endpoint_tenant_none(self):
        with self.assertRaises(EndpointException):
            CxOneAuthEndpoint(None, "foo.bar.com")
    
    async def test_auth_endpoint_server_none(self):
        with self.assertRaises(EndpointException):
            CxOneAuthEndpoint("None", None)

    async def test_auth_endpoint_scheme_none(self):
        with self.assertRaises(EndpointException):
            CxOneAuthEndpoint("None", "None", None)

    async def test_auth_endpoint_url_for_server_name(self):
        with self.assertRaises(EndpointException):
            CxOneAuthEndpoint("None", "https://foo.bar.com")

    async def test_valid_auth_endpoint(self):
        self.assertTrue(CxOneAuthEndpoint("None", "foo.bar.com"))

    async def test_api_endpoint_server_none(self):
        with self.assertRaises(EndpointException):
            CxOneApiEndpoint(None)

    async def test_api_endpoint_scheme_none(self):
        with self.assertRaises(EndpointException):
            CxOneApiEndpoint("None", None)

    async def test_api_endpoint_url_for_server_name(self):
        with self.assertRaises(EndpointException):
            CxOneApiEndpoint("https://foo.bar.com")

    async def test_valid_api_endpoint(self):
        self.assertTrue(CxOneApiEndpoint("foo.bar.com"))


if __name__ == "__main__":
    unittest.main()

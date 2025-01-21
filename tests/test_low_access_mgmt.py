import unittest
import cxone_api.low.access_mgmt.user_mgmt as um
from tests import BaseTest

class TestLowAccessMgmt(BaseTest):
    
    async def test_canary(self):
        self.assertTrue(1 == 1)

    async def test_retrieve_users_groups(self):
        await self.execute_client_call(um.retrieve_users_groups, self.assert_response_ok)
    
    async def test_retrieve_groups(self):
        await self.execute_client_call(um.retrieve_groups, self.assert_response_ok)

    async def test_retrieve_users(self):
        await self.execute_client_call(um.retrieve_users, self.assert_response_ok)

    async def test_retrieve_clients(self):
        await self.execute_client_call(um.retrieve_clients, self.assert_response_ok)

if __name__ == "__main__":
    unittest.main()

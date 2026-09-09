import unittest
from cxone_api.low.policy_management import retrieve_all_policies
from tests import BaseTest

class TestLowPolicyManagement(BaseTest):
    
    async def test_canary(self):
        self.assertTrue(1 == 1)
    
    async def test_retrieve_policies(self):
        await self.execute_client_call(retrieve_all_policies, self.assert_response_ok, { "page" : 1})

if __name__ == "__main__":
    unittest.main()

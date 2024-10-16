import unittest
from cxone_api.low.iam import retrieve_groups
from tests import BaseTest

class TestLowIAM(BaseTest):
    
    async def test_canary(self):
        self.assertTrue(1 == 1)
    
    async def test_retrieve_groups(self):
        await self.execute_client_call(retrieve_groups, self.assert_response_ok)

if __name__ == "__main__":
    unittest.main()

import unittest
from cxone_api.low.policy_management import retrieve_all_policies
from cxone_api.util import page_generator
from cxone_api import CxOneClient
from tests import BaseTest

class TestUtil(BaseTest):

    def __eval_true_return(self, result : bool, client : CxOneClient):
        self.assertTrue(result)
    
    async def test_canary(self):
        self.assertTrue(1 == 1)
    
    async def test_page_generator_with_expected_element(self):
        async def run_test(client : CxOneClient) -> bool:
            try:
              async for x in page_generator(retrieve_all_policies, "policies", "page", 1, False, client = client):
                  pass
            except Exception:
              return False

            return True
        
        await self.execute_client_call(run_test, self.__eval_true_return)

    async def test_page_generator_with_unexpected_element(self):
        async def run_test(client : CxOneClient) -> bool:
            try:
              async for x in page_generator(retrieve_all_policies, "wrong", "page", 1, False, client = client):
                  pass
            except Exception:
              return False

            return True
        
        await self.execute_client_call(run_test, self.__eval_true_return)

if __name__ == "__main__":
    unittest.main()

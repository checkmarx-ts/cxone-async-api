from tests import BaseTest
from cxone_api.high.access_mgmt.user_mgmt import Groups
from cxone_api.util import json_on_ok

class TestHighGroups(BaseTest):
    async def test_canary(self):
        self.assertTrue(1 == 1)

    async def test_group_list(self):
        async def execute_test(client):
            g = Groups(client)
            return await g.get_path_list()

        async def eval_group_list(glist, client):
            self.assertIsNotNone(glist)
            
        await self.execute_client_call(execute_test, eval_group_list)
        

from tests import BaseTest
import uuid
import cxone_api.low.scans as scans
import cxone_api.low.projects as projs
from cxone_api.util import json_on_ok

class TestLowScans(BaseTest):
    
    async def asyncSetUp(self):
        self.__delete_projects = []


    async def asyncTearDown(self):
        for projid in self.__delete_projects:
            await projs.delete_a_project(self.client_oauth, projid)

    
    async def create_project(self, client, repoUrl=BaseTest.DEFAULT_REPO, mainBranch=BaseTest.DEFAULT_BRANCH):
        name = str(uuid.uuid4())
        response = await projs.create_a_project(client, name=name, repoUrl=repoUrl, mainBranch=mainBranch)
        result = json_on_ok(response)
        self.__delete_projects.append(result['id'])
        return response


    async def test_canary(self):
        self.assertTrue(1 == 1)


    async def test_run_a_scan(self):

        async def validate_scan_run(response, client):
            scanid = json_on_ok(response)['id']
            self.assertTrue(await self.wait_for_scan_completion(client, scanid))
            pass

        async def make_scan_payload():
            return {
                "project" : {"id" : json_on_ok(await self.create_project(self.client_oauth))['id']},
                "type" : "git",
                "handler" : {
                    "repoUrl" : BaseTest.DEFAULT_REPO,
                    "branch" : BaseTest.DEFAULT_BRANCH
                },
                "config" : [
                    {
                        "type" : "sast", "value" : {},
                    },
                    {
                        "type" : "sca", "value" : {},
                    }
                ]
            }

        await self.execute_client_call(scans.run_a_scan, validate_scan_run, {"payload" : make_scan_payload})


import uuid, asyncio
import cxone_api.low.projects as projs
from cxone_api.high.scans import ScanInvoker
from cxone_api.high.projects import ProjectRepoConfig
from cxone_api.util import json_on_ok
from tests import BaseTest



class TestLowProjects(BaseTest):

    
    async def asyncSetUp(self):
        self.__delete_projects = []


    async def asyncTearDown(self):
        for projid in self.__delete_projects:
            await projs.delete_a_project(self.client_oauth, projid)

    
    async def __create_project(self, client, repoUrl=BaseTest.DEFAULT_REPO, mainBranch=BaseTest.DEFAULT_BRANCH):
        name = str(uuid.uuid4())
        response = await projs.create_a_project(client, name=name, repoUrl=repoUrl, mainBranch=mainBranch)
        result = json_on_ok(response)
        self.__delete_projects.append(result['id'])
        return response
    
    async def test_canary(self):
        self.assertTrue(1 == 1)

    async def test_create_project(self):
        await self.execute_client_call(self.__create_project, self.assert_response_ok)
    
    async def test_project_list_all(self):
        projid = json_on_ok(await self.__create_project(self.client_oauth))['id']

        async def validate_proj_in_list(response, client):
            projects = [x['id'] for x in json_on_ok(response)['projects']]
            self.assertIn(projid, projects)

        await self.execute_client_call(projs.retrieve_list_of_projects, validate_proj_in_list)

    async def test_project_list_by_name_regex(self):
        result = json_on_ok(await self.__create_project(self.client_oauth))
        projname = result['name']
        projid = result['id']

        async def validate_proj_in_list(response, client):
            projects = [x['id'] for x in json_on_ok(response)['projects']]
            self.assertIn(projid, projects)

        await self.execute_client_call(projs.retrieve_list_of_projects, validate_proj_in_list, {"name_regex" : lambda: f"{projname[0:5]}.*" })

    async def test_get_project_tags_list(self):
        result = json_on_ok(await self.__create_project(self.client_oauth))
        projid = result['id']

        async def validate_proj_tag_in_list(response, client):
            self.assertTrue(set(["foo", "bar"]) == set(json_on_ok(response).keys()))

        result['tags'] = {"foo" : "bar", "bar" : ""}

        response = await projs.update_a_project(self.client_oauth, projid, **result)

        await self.execute_client_call(projs.retrieve_list_of_tags, validate_proj_tag_in_list)
        self.assertTrue(response.ok)

    async def test_get_project_last_scan_no_scans(self):
        projid = json_on_ok(await self.__create_project(self.client_oauth))['id']

        async def validate_no_scans(response, client):
            self.assertTrue(len(json_on_ok(response)) == 0)

        await self.execute_client_call(projs.retrieve_last_scan, validate_no_scans, {"project_ids" : lambda: [projid]})

    async def __make_scan(self, projid):
        return await ScanInvoker.scan_get_scanid(self.client_oauth, await ProjectRepoConfig.from_project_id(self.client_oauth, projid),
                                                BaseTest.DEFAULT_BRANCH, ['sast', 'sca'])
    


    async def test_get_project_last_finished_scan(self):
        projid = json_on_ok(await self.__create_project(self.client_oauth))['id']
        scanid = await self.__make_scan(projid)

        async def validate_scan(response, client):
            result = json_on_ok(response)
            if not(projid in result.keys() and result[projid]['id'] == scanid):
                self.fail(f"Expected {scanid} as the last scan.")
           
            self.assertTrue(await self.wait_for_scan_completion(client, scanid))


        await self.execute_client_call(projs.retrieve_last_scan, validate_scan, {"project_ids" : lambda: [projid]})

    async def test_get_project_get_branches_no_scans(self):
        projid = json_on_ok(await self.__create_project(self.client_oauth))['id']
        
        async def validate_branches(response, client):
            self.assertIs(json_on_ok(response), None)

        await self.execute_client_call(projs.retrieve_list_of_branches, validate_branches, {"project_id" : lambda: projid})

    async def test_get_project_get_branches_with_scan(self):
        projid = json_on_ok(await self.__create_project(self.client_oauth))['id']
        scanid = await self.__make_scan(projid)

        async def validate_branches(response, client):
            self.assertTrue(await self.wait_for_scan_completion(client, scanid) and BaseTest.DEFAULT_BRANCH in json_on_ok(response))

        await self.execute_client_call(projs.retrieve_list_of_branches, validate_branches, {"project_id" : lambda: projid})

    async def test_get_project_info(self):
        projid = json_on_ok(await self.__create_project(self.client_oauth))['id']

        async def validate_project_info(response, client):
            result = json_on_ok(response)
            self.assertTrue(result['id'] == projid)

        await self.execute_client_call(projs.retrieve_project_info, validate_project_info, {"projectid" : lambda: projid})



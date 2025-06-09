import unittest
import uuid
import cxone_api.low.applications as apps
from cxone_api.exceptions import ResponseException
from cxone_api.util import page_generator, json_on_ok
from tests import BaseTest


class TestLowApplications(BaseTest):

    DEFAULT_APP_NAME = "DELETE_ME_APP"

    async def asyncSetUp(self):
        self.__delete_app_names = []
        
        apps_resp = await apps.retrieve_applications_info(self.client_oauth, 
                        name=TestLowApplications.DEFAULT_APP_NAME)

        if apps_resp.ok and len(apps_resp.json()['applications']) == 0:
            app_create_resp = await apps.create_an_application(self.client_oauth,
                                name=TestLowApplications.DEFAULT_APP_NAME,
                                description="regression testing purposes")
            if app_create_resp.ok:
                self.__appid = app_create_resp.json()['id']
            else:
                raise ResponseException("Unknown response creating an application:" \
                        f"{app_create_resp}")
        else:
            self.__appid = apps_resp.json()['applications'][0]['id']



            

    async def asyncTearDown(self):
        async for appinfo in page_generator(apps.retrieve_applications_info, 
                'applications', client=self.client_oauth):
            if appinfo['name'] in self.__delete_app_names:
                await apps.delete_an_application(self.client_oauth, appinfo['id'])

        self.__delete_app_names = []

    def __gen_app_name(self):
        app_name = str(uuid.uuid4())
        self.__delete_app_names.append(app_name)
        return app_name

    def __gen_app_name_no_record(self):
        return str(uuid.uuid4())


    async def test_canary(self):
        self.assertTrue(1 == 1)

    async def test_create_an_application(self):
        await self.execute_client_call(apps.create_an_application, self.assert_response_ok, kwarg_generators = {'name' : self.__gen_app_name})

    async def test_retrieve_applications_info(self):
        await self.execute_client_call(apps.retrieve_applications_info, self.assert_response_ok)
    
    async def test_retrieve_list_of_tags(self):
        await self.execute_client_call(apps.retrieve_list_of_tags, self.assert_response_ok)

    async def test_retrieve_an_application(self):
        await self.execute_client_call(apps.retrieve_an_application, self.assert_response_ok, None, self.__appid)
        
    async def test_update_an_application(self):
        await self.execute_client_call(apps.update_an_application, self.assert_response_ok, {'criticality' : lambda: 1}, self.__appid)

    async def test_delete_an_application(self):
        try:

            async def delete_app_id(response, client):
                appid = json_on_ok(response)['id']
                self.assert_response_ok(await apps.delete_an_application(client, appid), client)

            await self.execute_client_call(apps.create_an_application, delete_app_id, kwarg_generators = {'name' : self.__gen_app_name_no_record})
        except ResponseException as ex:
            self.fail(ex)
        
        self.assertTrue(1 == 1)

    async def test_create_app_rule(self):
        await self.execute_client_call(apps.create_an_application_rule, self.assert_response_ok, 
                                       kwarg_generators = {'app_id' : lambda: self.__appid, 'type' : lambda: "project.tag.key.exists",
                                                           'value' : lambda: "foo"})

    async def test_delete_app_rule(self):
        async def on_app_create(response, client):
            appid = json_on_ok(response)['id']
            ruleid = json_on_ok(await apps.create_an_application_rule(client, appid, type = "project.tag.key.exists",
                                                           value="foo"))['id']
            response = await apps.delete_an_application_rule(client, appid, ruleid)
            self.assertTrue(response.ok)

        await self.execute_client_call(apps.create_an_application, on_app_create, kwarg_generators = {'name' : self.__gen_app_name_no_record})
        
    async def test_rule_appears_in_list(self):
        async def on_app_create(response, client):
            appid = json_on_ok(response)['id']
            ruleid = json_on_ok(await apps.create_an_application_rule(client, appid, type = "project.tag.key.exists",
                                                           value="foo"))['id']
           
            self.assertIn(ruleid, [x['id'] for x in json_on_ok(await apps.retrieve_list_of_application_rules(client, appid))])

        await self.execute_client_call(apps.create_an_application, on_app_create, kwarg_generators = {'name' : self.__gen_app_name_no_record})

    async def test_retrieve_app_rule(self):
        async def on_app_create(response, client):
            appid = json_on_ok(response)['id']
            ruleid = json_on_ok(await apps.create_an_application_rule(client, appid, type = "project.tag.key.exists",
                                                           value="foo"))['id']
            self.assertTrue(json_on_ok(await apps.retrieve_an_application_rule(client, appid, ruleid))['id'] == ruleid)

        await self.execute_client_call(apps.create_an_application, on_app_create, kwarg_generators = {'name' : self.__gen_app_name_no_record})


    async def test_update_app_rule(self):
        async def on_app_create(response, client):
            appid = json_on_ok(response)['id']
            ruleid = json_on_ok(await apps.create_an_application_rule(client, appid, type = "project.tag.key.exists",
                                                           value="foo"))['id']
            
            self.assertTrue((await apps.update_an_application_rule(client, appid, ruleid, type="project.tag.value.exists", value="bar")).ok)

        await self.execute_client_call(apps.create_an_application, on_app_create, kwarg_generators = {'name' : self.__gen_app_name_no_record})

if __name__ == "__main__":
    unittest.main()

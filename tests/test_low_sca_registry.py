import uuid, asyncio
from tests import BaseTest
from cxone_api.low.projects import create_a_project, delete_a_project
from cxone_api.low.sca.registry.configurations import (
    create_configuration,
    delete_configuration,
    retrieve_configurations,
    retrieve_configuration,
    modify_configuration,
    retrieve_project_configuration,
    associate_configurations_with_project,
    disassociate_configurations_from_project,
    retrieve_configurations_with_tag,
    associate_configurations_with_tag,
    disassociate_configurations_from_tag,
)
from cxone_api.low.sca.registry.projects import (
    retrieve_configurations_by_project,
    retrieve_projects_associated_with_configuration,
    disassociate_all_projects_from_configuration,
    associate_projects_with_configuration,
)
from cxone_api.low.sca.registry.tags import (
    retrieve_list_of_configurations_by_tag,
    create_configuration_tag,
    retrieve_tag_details,
    modify_tag_name,
    delete_tag,
    retrieve_tags_of_configuration,
    associate_tags_with_configuration,
    disassociate_all_tags_from_configuration,
)
from cxone_api.util import json_on_ok, page_generator


# TODO: This API is unstable, turn off the unit testing for now.
# class TestLowScaRegistry(BaseTest):
#     async def test_canary(self):
#         self.assertTrue(1 == 1)

#     __NUGET = """
# <?xml version="1.0" encoding="utf-8"?>
# <configuration>
#   <packageSources>
#     <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />
#   </packageSources>
# </configuration>
#     """

#     async def asyncSetUp(self):
#         self.__delete_cfgs = []

#     async def asyncTearDown(self):
#         for cfgid in self.__delete_cfgs:
#             await delete_a_configuration(self.client_oauth, cfgid)

#     async def __create_configuration(self, client) -> str:
#         while True:
#             create_response = await create_a_configuration(
#                 client, str(uuid.uuid4()), "nuget", TestLowScaRegistry.__NUGET
#             )
#             if not create_response.ok and create_response.status_code == 400:
#                 await asyncio.sleep(3)
#             elif create_response.ok:
#                 break

#         create_result = json_on_ok(create_response)

#         self.__delete_cfgs.append(create_result.get("id"))
#         return create_result.get("id")

#     def assert_id_not_none(self, id, _):
#         self.assertIsNotNone(id)

#     async def test_create_configuration(self):
#         await self.execute_client_call(
#             self.__create_configuration, self.assert_id_not_none
#         )

#     async def test_delete_configuration(self):
#         cfgs = await self.execute_client_call(
#             self.__create_configuration, self.assert_id_not_none
#         )

#         for cfg in cfgs:
#             self.assertTrue((await delete_a_configuration(self.client_oauth, cfg)).ok)

#     async def test_retrieve_configurations(self):
#         cfgs = await self.execute_client_call(
#             self.__create_configuration, self.assert_id_not_none
#         )

#         async def __get_cfgs(client):
#             async for cfg in page_generator(
#                 retrieve_configurations,
#                 offset_param="PageNumber",
#                 offset_init_value=1,
#                 offset_is_by_count=False,
#                 client=client,
#                 PageSize=1,
#             ):
#                 pass

#             return True

#         await self.execute_client_call(
#             __get_cfgs, lambda result, client: self.assertTrue(result)
#         )

#     async def test_retrieve_a_configurations(self):
#         cfgs = await self.execute_client_call(
#             self.__create_configuration, self.assert_id_not_none
#         )

#         for cfg in cfgs:
#             await self.execute_client_call(
#                 retrieve_a_configuration, self.assert_response_ok, {"configId": cfg}
#             )

#     async def test_modify_a_configuration(self):
#         cfgs = await self.execute_client_call(
#             self.__create_configuration, self.assert_id_not_none
#         )

#         for cfg in cfgs:
#             await self.execute_client_call(
#                 modify_a_configuration,
#                 self.assert_response_ok,
#                 {
#                     "configId": cfg,
#                     "packageManager": "nuget",
#                     "configurationName": str(uuid.uuid4()),
#                     "content": TestLowScaRegistry.__NUGET,
#                 },
#             )

#     async def test_associate_retrieve_disassociate_project_configuration(self):
#         prjid = json_on_ok(
#             await create_a_project(self.client_oauth, name=str(uuid.uuid4()))
#         ).get("id")

#         cfgid = await self.__create_configuration(self.client_oauth)

#         await self.execute_client_call(
#             associate_configurations_with_project,
#             self.assert_response_ok,
#             {"projectId": prjid, "configurationIds": [cfgid]},
#         )

#         await self.execute_client_call(
#             retrieve_a_project_configuration,
#             self.assert_response_ok,
#             {"projectId": prjid},
#         )

#         await self.execute_client_call(
#             disassociate_configurations_from_project,
#             self.assert_response_ok,
#             {"projectId": prjid, "configurationIds": [cfgid]},
#         )

#         await delete_a_project(self.client_oauth, prjid)

#     async def test_associate_retrieve_disassociate_configuration_tag(self):
#         tagid = json_on_ok(
#             await create_configuration_tag(self.client_oauth, name=str(uuid.uuid4()))
#         ).get("id")

#         cfgid = await self.__create_configuration(self.client_oauth)

#         await self.execute_client_call(
#             associate_configurations_with_tag,
#             self.assert_response_ok,
#             {"tagId": tagid, "configurationIds": [cfgid]},
#         )

#         await self.execute_client_call(
#             retrieve_configurations_with_tag,
#             self.assert_response_ok,
#             {"tagId": tagid},
#         )

#         await self.execute_client_call(
#             disassociate_configurations_from_tag,
#             self.assert_response_ok,
#             {"tagId": tagid},
#         )

#         self.assertTrue((await delete_tag(self.client_oauth, tagid)).ok)

#     async def test_associate_retrieve_by_projects(self):
#         cfgs = await self.execute_client_call(
#             self.__create_configuration, self.assert_id_not_none
#         )

#         prjid = json_on_ok(
#             await create_a_project(self.client_oauth, name=str(uuid.uuid4()))
#         ).get("id")

#         for cfg in cfgs:
#             await associate_projects_with_configuration(self.client_oauth, cfg, [prjid])

#         async def __get_cfgs(client):
#             async for cfg in page_generator(
#                 retrieve_configurations_by_project,
#                 offset_param="PageNumber",
#                 offset_init_value=1,
#                 offset_is_by_count=False,
#                 client=client,
#                 PageSize=1,
#             ):
#                 pass

#             return True

#         await self.execute_client_call(
#             __get_cfgs, lambda result, client: self.assertTrue(result)
#         )

#         await delete_a_project(self.client_oauth, prjid)

#     async def test_associate_retrieve_disassociate_project(self):
#         cfgs = await self.execute_client_call(
#             self.__create_configuration, self.assert_id_not_none
#         )

#         prjid = json_on_ok(
#             await create_a_project(self.client_oauth, name=str(uuid.uuid4()))
#         ).get("id")

#         for cfg in cfgs:
#             await associate_projects_with_configuration(self.client_oauth, cfg, [prjid])
#             await self.execute_client_call(
#                 retrieve_projects_associated_with_configuration,
#                 self.assert_response_ok,
#                 {"configId": cfg},
#             )

#         for cfg in cfgs:
#             self.assertTrue(
#                 (
#                     await disassociate_all_projects_from_configuration(
#                         self.client_oauth, cfg
#                     )
#                 ).ok
#             )

#         await delete_a_project(self.client_oauth, prjid)

#     async def test_associate_retrieve_disassociate_tag(self):
#         cfgs = await self.execute_client_call(
#             self.__create_configuration, self.assert_id_not_none
#         )

#         tagid = json_on_ok(
#             await create_configuration_tag(self.client_oauth, name=str(uuid.uuid4()))
#         ).get("id")

#         for cfg in cfgs:
#             await self.execute_client_call(
#                 associate_tags_with_configuration,
#                 self.assert_response_ok,
#                 {"configId": cfg, "tags": [tagid]},
#             )

#             await self.execute_client_call(
#                 retrieve_tags_of_configuration,
#                 self.assert_response_ok,
#                 {"configId": cfg},
#             )

#         async def __get_cfgs(client):
#             async for cfg in page_generator(
#                 retrieve_list_of_configurations_by_tag,
#                 offset_param="PageNumber",
#                 offset_init_value=1,
#                 offset_is_by_count=False,
#                 client=client,
#                 PageSize=1,
#             ):
#                 pass

#             return True

#         await self.execute_client_call(
#             __get_cfgs, lambda result, client: self.assertTrue(result)
#         )

#         for cfg in cfgs:
#             self.assertTrue(
#                 (
#                     await disassociate_all_tags_from_configuration(
#                         self.client_oauth, cfg
#                     )
#                 ).ok
#             )


#     async def test_create_read_modify_tag(self):
#         tagid = json_on_ok(
#             await create_configuration_tag(self.client_oauth, name=str(uuid.uuid4()))
#         ).get("id")

#         await self.execute_client_call(
#             retrieve_tag_details, self.assert_response_ok, {"tagId": tagid}
#         )

#         await self.execute_client_call(
#             modify_tag_name,
#             self.assert_response_ok,
#             {"tagId": tagid, "name": str(uuid.uuid4())},
#         )

#         self.assertTrue((await delete_tag(self.client_oauth, tagid)).ok)

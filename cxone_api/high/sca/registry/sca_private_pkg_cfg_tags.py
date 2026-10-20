from __future__ import annotations
from typing import Dict
from cxone_api import CxOneClient
from cxone_api.low.sca.registry.tags import (
    create_configuration_tag,
    retrieve_tag_details,
    modify_tag_name,
    delete_tag,
)
from cxone_api.util import json_on_ok


class PackageRepositoryConfigurationTag:

    @staticmethod
    async def create_new(
        client: CxOneClient, name: str
    ) -> PackageRepositoryConfigurationTag:
        inst = PackageRepositoryConfigurationTag()
        new_tag = json_on_ok(await create_configuration_tag(client, name))
        inst.__client = client
        inst.__id = new_tag.get("id")
        inst.__name = name
        return inst

    @staticmethod
    def from_tag_json(
        client: CxOneClient, json: Dict
    ) -> PackageRepositoryConfigurationTag:
        inst = PackageRepositoryConfigurationTag()
        inst.__id = json.get("id")
        inst.__name = json.get("name")
        inst.__client = client
        return inst

    @staticmethod
    async def retrieve_by_id(
        client: CxOneClient, tagId: str
    ) -> PackageRepositoryConfigurationTag:
        inst = PackageRepositoryConfigurationTag()
        tag = json_on_ok(await retrieve_tag_details(client, tagId))
        inst.__id = tag.get("id")
        inst.__name = tag.get("name")
        inst.__client = client
        return inst

    def __repr__(self):
        return f"{self.tagid}:{self.name}"

    @property
    def name(self) -> str:
        return self.__name

    @property
    def tagid(self) -> str:
        return self.__id

    async def change_name(self, new_name: str) -> bool:
        if (await modify_tag_name(self.__client, self.tagid, new_name)).ok:
            self.__name = new_name
            return True

        return False

    async def delete(self) -> bool:
        if (await delete_tag(self.__client, self.__id)).ok:
            return True

        return False

import asyncio
from cxone_api.util import CloneUrlParser, json_on_ok
from cxone_api import CxOneClient
from cxone_api.low.projects import retrieve_last_scan, retrieve_project_info
from cxone_api.low.scan_configuration import retrieve_project_configuration
from cxone_api.low.repos_manager import get_scm_by_id, retrieve_repo_by_id
from typing import List


class ProjectRepoConfig:
    """A class that allows inspection of a project's repository configuration."""

    def __common_init(self, cxone_client: CxOneClient):
        self.__client = cxone_client
        self.__fetched_scan_config = False
        self.__fetched_repomgr_config = False
        self.__fetched_scm_config = False
        self.__is_imported = False
        self.__lock = asyncio.Lock()

    @staticmethod
    async def from_project_json(cxone_client: CxOneClient, json: dict):
        """A factory method to create an instance from the JSON retrieved with the retrieve_project_info API.

           :param cxone_client: The CxOneClient instance used to communicate with Checkmarx One
           :type cxone_client: CxOneClient

           :param json: A JSON dictionary.
           :type json: dict

           :rtype: ProjectRepoConfig
        """
        retval = ProjectRepoConfig()
        ProjectRepoConfig.__common_init(retval, cxone_client)
        retval.__project_data = json
        retval.__is_imported = "repoId" in retval.__project_data.keys()

        return retval

    @staticmethod
    async def from_project_id(cxone_client: CxOneClient, project_id: str):
        """A factory method to create an instance using the project ID.

            :param cxone_client: The CxOneClient instance used to communicate with Checkmarx One.
            :type cxone_client: CxOneClient

            :param project_id: A project ID.
            :type project_id: str

            :rtype: ProjectRepoConfig
        """
        retval = ProjectRepoConfig()
        ProjectRepoConfig.__common_init(retval, cxone_client)
        retval.__project_data = json_on_ok(await retrieve_project_info(cxone_client, project_id))
        retval.__is_imported = "repoId" in retval.__project_data.keys()
        return retval

    def __getattr__(self, name):
        if name in self.__project_data.keys():
            return self.__project_data[name]
        else:
            raise AttributeError(name)

    async def get_project_scan_config(self):
        """Returns the project's scan configuration.

            :rtype: dict
        """
        async with self.__lock:
            if not self.__fetched_scan_config:
                self.__fetched_scan_config = True
                self.__scan_config = json_on_ok(await retrieve_project_configuration(self.__client, projectid=self.project_id))

        return self.__scan_config

    async def __get_repourl_from_scan_config(self):
        # The project config API does not always return the repoUrl.  The scan configuration
        # API used by the UI has it if it is not in the project config.
        for entry in await self.get_project_scan_config():
            if entry['key'] == "scan.handler.git.repository":
                return entry['value']

        return None

    async def __get_primary_branch_from_scan_config(self):
        # The project config API does not always return the repoUrl.  The scan configuration
        # API used by the UI has it if it is not in the project config.
        for entry in await self.get_project_scan_config():
            if entry['key'] == "scan.handler.git.branch":
                return entry['value']

        return ""

    async def __get_repomgr_config(self):
        # Projects imported from the SCM have their repo credentials stored in the repo-manager
        if not "repoId" in self.__project_data.keys():
            return None

        async with self.__lock:
            if not self.__fetched_repomgr_config:
                self.__fetched_repomgr_config = True
                repoId = self.__project_data['repoId']

                repo_response = await retrieve_repo_by_id(self.__client, repoId)
                if repo_response.ok:
                    self.__repomgr_config = repo_response.json()
                else:
                    self.__repomgr_config = None

        return self.__repomgr_config

    async def __get_repourl_from_repomgr_config(self):
        cfg = await self.__get_repomgr_config()

        if cfg is None:
            return ""
        else:
            return cfg['url']

    async def __get_primary_branch_from_repomgr_config(self):
        cfg = await self.__get_repomgr_config()

        if cfg is not None:
            if "branches" in cfg.keys():
                for b in cfg['branches']:
                    # Select the default branch as specified in the scm or the first branch
                    # if only one protected branch is specified.
                    if ("isDefaultBranch" in b.keys() and bool(b['isDefaultBranch'])) \
                            or len(cfg['branches']) == 1:
                        if "name" in b.keys():
                            return b['name']
        return ""

    async def __get_logical_repo_url(self):
        if len(await self.__get_repourl_from_repomgr_config()) > 0:
            return await self.__get_repourl_from_repomgr_config()
        elif len(self.__project_data['repoUrl']) > 0:
            return self.__project_data['repoUrl']
        elif len(await self.__get_repourl_from_scan_config()) > 0:
            return await self.__get_repourl_from_scan_config()
        else:
            return None

    async def __get_logical_primary_branch(self):
        if len(self.__project_data['mainBranch']) > 0:
            return self.__project_data['mainBranch']
        elif len(await self.__get_primary_branch_from_repomgr_config()) > 0:
            return await self.__get_primary_branch_from_repomgr_config()
        elif len(await self.__get_primary_branch_from_scan_config()):
            return await self.__get_primary_branch_from_scan_config()

        return None

    async def __get_scm_config(self):
        if not await self.is_scm_imported or await self.scm_creds_expired:
            return None

        this_scm_id = await self.scm_id

        async with self.__lock:
            if not self.__fetched_scm_config:
                self.__fetched_scm_config = True
                self.__scm_config = json_on_ok(await get_scm_by_id(self.__client, this_scm_id))

        return self.__scm_config

    @property
    async def primary_branch(self):
        """The configured primary branch."""
        return await self.__get_logical_primary_branch()

    @property
    async def repo_url(self):
        """The URL for the source repository."""
        url = await self.__get_logical_repo_url()
        return url if url is not None and len(url) > 0 else None

    @property
    async def is_scm_imported(self):
        """A boolean value indicating if the project was created using a code repository import."""
        return self.__is_imported

    @property
    async def scm_creds_expired(self):
        """A boolean value indicating if the SCM credentials have expired."""
        if not self.__is_imported:
            return True

        return await self.__get_repomgr_config() is None

    @property
    async def scm_id(self):
        """The internal ID of the SCM configuration."""
        if not await self.is_scm_imported or await self.scm_creds_expired:
            return None

        cfg = await self.__get_repomgr_config()

        if cfg is None:
            return None
        elif "scmId" in cfg.keys():
            return cfg['scmId']
        else:
            return None

    @property
    async def scm_org(self):
        """The organization in the SCM that owns the source repository associated with this project."""
        if not await self.is_scm_imported or await self.scm_creds_expired:
            return None

        return CloneUrlParser(await self.scm_type, await self.repo_url).org

    @property
    async def scm_type(self):
        """The type of SCM where this repository lives."""
        if not await self.is_scm_imported or await self.scm_creds_expired:
            return None

        cfg = await self.__get_scm_config()
        if cfg is None:
            return None
        elif "type" in cfg.keys():
            return cfg['type']
        else:
            return None

    @property
    async def repo_id(self):
        """The internal ID of the source repository configuration."""
        if not await self.is_scm_imported or await self.scm_creds_expired:
            return None

        return self.__project_data['repoId']

    @property
    async def scm_repo_id(self):
        """The internal ID of the source repository configuration."""
        if not await self.is_scm_imported or await self.scm_creds_expired:
            return None

        return self.__project_data['scmRepoId']

    @property
    def project_id(self):
        """The project ID."""
        return self.__project_data['id']

    async def get_enabled_scanners(self, by_branch: str) -> List[str]:
        """Retrieves the scanners that have been selected for scanning, if any.

            If the project was created as a code repository import, this returns a list of
            selected scan engines as set in the code repository configuration for the project.

            If the project is a manual scan project, the list of engines used in the latest
            scan for the specified branch are returned.  If no scans are found in the project
            for the specified branch, an empty list is returned.

            :param by_branch: The name of the branch used to retrieve the last scan.
            :type by_branch: str


            :rtype: List[str]
        """
        engines = []

        if await self.is_scm_imported and not await self.scm_creds_expired:
            # Use the engine configuration on the import
            cfg = await self.__get_repomgr_config()

            for k in cfg.keys():
                if k.lower().endswith("scannerenabled") and bool(cfg[k]):
                    engines.append(k.lower().removesuffix("scannerenabled"))

        if len(engines) == 0:
            # If no engines configured by the import config, use the engines for the last scan.
            last_scan = json_on_ok(await retrieve_last_scan(self.__client, project_ids=[self.project_id], branch=by_branch, limit=1))
            if len(last_scan) > 0:
                latest_scan_header = list(last_scan.values())[0]
                if 'engines' in latest_scan_header.keys():
                    engines = latest_scan_header['engines']

        return engines

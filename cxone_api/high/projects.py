import asyncio
from ..util import CloneUrlParser, json_on_ok
from .. import CxOneClient
from ..low.projects import retrieve_last_scan, retrieve_project_info
from ..low.scan_configuration import retrieve_project_configuration
from ..low.repos_manager import get_scm_by_id, retrieve_repo_by_id

class ProjectRepoConfig:

    def __common_init(self, cxone_client : CxOneClient):
        self.__client = cxone_client
        self.__fetched_scan_config = False
        self.__fetched_repomgr_config = False
        self.__fetched_scm_config = False
        self.__lock = asyncio.Lock()

    @staticmethod
    async def from_project_json(cxone_client : CxOneClient, json : dict):
        retval = ProjectRepoConfig()
        ProjectRepoConfig.__common_init(retval, cxone_client)
        retval.__project_data = json

        return retval

    @staticmethod
    async def from_project_id(cxone_client : CxOneClient, project_id : str):
        retval = ProjectRepoConfig()
        ProjectRepoConfig.__common_init(retval, cxone_client)
        retval.__project_data = json_on_ok(await retrieve_project_info(cxone_client, project_id))
        return retval
 

    def __getattr__(self, name):
        if name in self.__project_data.keys():
            return self.__project_data[name]
        else:
            raise AttributeError(name)
        

    async def get_project_scan_config(self):
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

    async def __get_repomgr_config(self):
        # Projects imported from the SCM have their repo credentials stored in the repo-manager
        if not "repoId" in self.__project_data.keys(): 
            return None

        async with self.__lock:
            if not self.__fetched_repomgr_config:
                self.__fetched_repomgr_config = True
                repoId = self.__project_data['repoId']
                self.__repomgr_config = json_on_ok(await retrieve_repo_by_id(self.__client, repoId))
        
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

        return None
    
    async def __get_scm_config(self):
        if not await self.is_scm_imported:
            return None
        
        this_scm_id = await self.scm_id
        
        async with self.__lock:
            if not self.__fetched_scm_config:
                self.__fetched_scm_config = True
                self.__scm_config = json_on_ok(await get_scm_by_id(self.__client, this_scm_id))
        
        return self.__scm_config
        
    @property
    async def primary_branch(self):
        return await self.__get_logical_primary_branch()

    @property
    async def repo_url(self):
        url = await self.__get_logical_repo_url()
        return url if url is not None and len(url) > 0 else None
    
    @property
    async def is_scm_imported(self):
        return await self.__get_repomgr_config() is not None


    @property
    async def scm_id(self):
        if not await self.is_scm_imported:
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
        if not await self.is_scm_imported:
            return None

        return CloneUrlParser(await self.scm_type, await self.repo_url).org
        

    @property
    async def scm_type(self):
        if not await self.is_scm_imported:
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
        if not await self.is_scm_imported:
            return None
       
        return self.__project_data['repoId']

    @property
    async def scm_repo_id(self):
        if not await self.is_scm_imported:
            return None
       
        return self.__project_data['scmRepoId']


    @property
    def project_id(self):
        return self.__project_data['id']
    
    async def get_enabled_scanners(self, by_branch):
        engines = []

        if await self.is_scm_imported:
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


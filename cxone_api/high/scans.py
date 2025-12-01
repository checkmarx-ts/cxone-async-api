from typing import Union, List, Dict
from jsonpath_ng import parse
from requests import Response
from .projects import ProjectRepoConfig
from .. import CxOneClient
from ..util import json_on_ok
from ..exceptions import ScanException
from ..low.scan_configuration import retrieve_project_configuration
from ..low.scans import retrieve_scan_details, run_a_repo_scan, run_a_scan
from ..low.scan_configuration import retrieve_tenant_configuration
from ..low.uploads import generate_upload_link, upload_to_link
from .projects import ProjectRepoConfig
from enum import Enum
import asyncio, logging, deprecation

class ScanInvoker:
    """A class used to invoke scans using the various methods supported by Checkmarx One."""

    class CredentialTypeEnum(Enum):
        """An enumeration to specify the type of clone credential."""
        NONE = "None"
        APIKEY = "apiKey"
        PASSWORD = "password"
        SSH = "ssh"
        JWT = "JWT"

    __DEFAULT_ENGINE_CONFIG = [{"type" : "sast", "value" : {}}]

    @staticmethod
    @deprecation.deprecated(details="Use class methods that indicate the scan invocation method by name.")
    async def scan_get_response(cxone_client : CxOneClient, project_repo : ProjectRepoConfig,
                    branch : str, engine_config : Union[list,dict] = None , tags : dict = None,
                    src_zip_path : str = None, clone_user : str = None,
                    clone_cred_type : str = None, clone_cred_value : str = None) -> Response:
        """deprecated"""

        submit_payload = {}

        target_repo = await project_repo.repo_url

        if (not await project_repo.is_scm_imported) or (src_zip_path is not None) or \
            (clone_cred_value is not None):
            submit_payload["project"] = {"id" : project_repo.project_id}

            if src_zip_path is not None:
                submit_payload["handler"] = {"uploadUrl" :
                  await ScanInvoker.__upload_zip(cxone_client, src_zip_path)}
                submit_payload["type"] = "upload"
            else:
                submit_payload["type"] = "git"
                submit_payload["handler"] = {}


            submit_payload["handler"]["branch"] = "unknown" if branch is None else branch
            if not clone_cred_value is None and src_zip_path is None:
                submit_payload["handler"]["credentials"] = {
                    "username" : clone_user if clone_user is not None else "",
                    "type" : clone_cred_type,
                    "value" : clone_cred_value
                }


            if isinstance(engine_config, list):
                submit_payload["config"] = [{ "type" : x, "value" : {} } for x in engine_config] \
                    if engine_config is not None else {}
            elif isinstance(engine_config, dict):
                submit_payload["config"] = [{ "type" : x, "value" : {} if engine_config[x] is None \
                                             else engine_config[x]} for x in engine_config] \
                                             if engine_config is not None else {}

            if tags is not None:
                submit_payload["tags"] = tags

            if target_repo is not None:
                submit_payload["handler"]["repoUrl"] = target_repo

            return  await run_a_scan(cxone_client, submit_payload)
        else:

            if isinstance(engine_config, list):
                scanner_types = engine_config if engine_config is not None else []
            elif isinstance(engine_config, dict):
                scanner_types = list(engine_config.keys())

            submit_payload["repoOrigin"] = await project_repo.scm_type
            submit_payload["project"] = {
                "repoIdentity" : await project_repo.scm_repo_id,
                "repoUrl" : await project_repo.repo_url,
                "projectId" : project_repo.project_id,
                "defaultBranch" : branch,
                "scannerTypes" : scanner_types,
                "repoId" : await project_repo.repo_id
            }

            scm_org = await project_repo.scm_org

            return await run_a_repo_scan(cxone_client, await project_repo.scm_id,
                        project_repo.project_id,
                        scm_org if scm_org is not None else "anyorg", submit_payload)

    @staticmethod
    @deprecation.deprecated(details="Use class methods that indicate the scan invocation method by name.")
    async def scan_get_scanid(cxone_client : CxOneClient, project_repo : ProjectRepoConfig,
                              branch : str, engines : list = None , tags : dict = None,
                              src_zip_path : str = None, clone_user : str = None,
                              clone_cred_type : str = None, clone_cred_value : str = None) -> str:
        """deprecated"""

        response = await ScanInvoker.scan_get_response(cxone_client, project_repo, branch, engines,
                              tags, src_zip_path, clone_user, clone_cred_type, clone_cred_value)

        if not response.ok:
            raise ScanException(f"Scan error for project {project_repo.project_id}: "
                                f"Status: {response.status_code} : {response.json()}")

        response_json = response.json()

        return response_json['id'] if "id" in response_json.keys() else None
    
    @staticmethod
    async def __get_logical_engine_config(client : CxOneClient, repo_config : ProjectRepoConfig, engine_config : List[Dict], branch : str) -> List[Dict]:
        if engine_config is not None:
            return engine_config
        elif len(await repo_config.get_enabled_scanners(branch)) > 0:
            return [{"type" : eng, "value" : {}} for eng in await repo_config.get_enabled_scanners(branch)]
        else:
            return ScanInvoker.__DEFAULT_ENGINE_CONFIG


    @staticmethod
    async def scan_by_local_zip_upload(client : CxOneClient, project_id : str, src_zip_path : str, branch : str, 
                                       engine_config : List[Dict] = None, scan_tags : dict = None) -> Response:
        """Invokes a scan by uploading a local zip file.
        
        :param client: The CxOneClient instance used to communicate with Checkmarx One
        :type client: CxOneClient

        :param project_id: The project ID where the scan will be invoked.
        :type project_id: str

        :param src_zip_path: A path to a local zip file to be uploaded for scanning.
        :type src_zip_path: str or path-like

        :param branch: The name of the branch used when performing the scan.
        :type branch: str

        :param engine_config: A list of JSON dictionaries containing the engine configuration parameters
        :type engine_config: List[Dict],optional

        :param scan_tags: A list of key/value pairs to use as scan tags.
        :type scan_tags: Dict,optional

        """
        
        effective_engine_config = engine_config
        if engine_config is None:
            effective_engine_config = await ScanInvoker.__get_logical_engine_config(client, 
                                                                                    await ProjectRepoConfig.from_project_id(client, project_id),
                                                                                    engine_config, branch)
        submit_payload = { "project" : {"id": project_id},
                            "type" : "upload",
                            "handler" : 
                                { 
                                    "uploadUrl" : await ScanInvoker.__upload_zip(client, src_zip_path),
                                    "branch" : "unknown" if branch is None else branch
                                },
                                "config" : effective_engine_config
                         }
        
        if scan_tags is not None:
            submit_payload["tags"] = scan_tags

        return await run_a_scan(client, submit_payload)

    @staticmethod
    async def scan_by_project_config(client : CxOneClient, project_id : str, branch : str = None, 
                                     engine_config : List[Dict] = None, scan_tags : dict = None ) -> Response:
        """Invokes a scan for projects created by a repository import.

        :param client: The CxOneClient instance used to communicate with Checkmarx One
        :type client: CxOneClient

        :param project_id: The project ID where the scan will be invoked.
        :type project_id: str

        :param branch: The name of the branch used when performing the scan. Uses the default branch if not provided.
        :type branch: str,optional

        :param engine_config: A list of JSON dictionaries containing the engine configuration parameters
        :type engine_config: List[Dict],optional

        :param scan_tags: A list of key/value pairs to use as scan tags.
        :type scan_tags: Dict,optional

        """
        repo_cfg = await ProjectRepoConfig.from_project_id(client, project_id)

        if await repo_cfg.primary_branch is None and branch is None:
            raise ScanException("Branch was not provided and no primary branch is configured in the project's general settings.")
        else:
            effective_branch = branch if branch is not None else await repo_cfg.primary_branch
        
        if await repo_cfg.repo_url is None:
            raise ScanException("There is no repository URL configured in the project's general settings.")

        submit_payload = {
            "project" : {"id" : project_id}
            }
        
        if scan_tags is not None:
            submit_payload['tags'] = scan_tags

        if not await repo_cfg.is_scm_imported:
            submit_payload['type'] = "git"
            submit_payload['handler'] = {}
            submit_payload['config'] = await ScanInvoker.__get_logical_engine_config(client, repo_cfg, engine_config, branch)


            submit_payload['handler']['branch'] = effective_branch
            submit_payload['handler']['repoUrl'] = await repo_cfg.repo_url
            
            return await run_a_scan(client, submit_payload)
        else:
            if engine_config is not None:
                enabled_scanners = [x['type'] for x in engine_config]
            else:
                enabled_scanners = await repo_cfg.get_enabled_scanners(effective_branch)
            
            submit_payload["repoOrigin"] = await repo_cfg.scm_type
            submit_payload["project"] = {
                "repoIdentity" : await repo_cfg.scm_repo_id,
                "repoUrl" : await repo_cfg.repo_url,
                "projectId" : project_id,
                "defaultBranch" : effective_branch,
                "scannerTypes" : enabled_scanners,
                "repoId" : await repo_cfg.repo_id
            }

            scm_org = await repo_cfg.scm_org

            return await run_a_repo_scan(client, 
                                         await repo_cfg.scm_id,
                                         project_id,
                                         scm_org \
                                           if scm_org is not None else "anyorg", 
                                         submit_payload)


    @staticmethod
    async def scan_by_clone_url(client : CxOneClient, project_id : str, clone_url : str, branch : str = None,
                                clone_user : str = None, clone_cred_type : CredentialTypeEnum = CredentialTypeEnum.NONE, clone_cred_value : str = None,  
                                engine_config : List[Dict] = None , scan_tags : dict = None) -> Response:
        """Invokes a scan using a clone URL.

                
        :param client: The CxOneClient instance used to communicate with Checkmarx One
        :type client: CxOneClient

        :param project_id: The project ID where the scan will be invoked.
        :type project_id: str

        :param clone_url: The clone URL appropriate for the type of clone credential.
        :type clone_url: str

        :param branch: The name of the branch used when performing the scan. Uses the default branch if not provided.
        :type branch: str,optional

        :param clone_user: The username matching the credential for the clone.
        :type clone_user: str,optional

        :param clone_cred_type: The type of clone credential to use for the clone.
        :type clone_cred_type: CredentialTypeEnum

        :param clone_cred_value: The clone credential that matches the indicated type of credential.
        :type clone_cred_value: str

        :param engine_config: A list of JSON dictionaries containing the engine configuration parameters
        :type engine_config: List[Dict],optional

        :param scan_tags: A list of key/value pairs to use as scan tags.
        :type scan_tags: Dict,optional

        """
        
        if engine_config is None or branch is None:
            repo_config = await ProjectRepoConfig.from_project_id(client, project_id)
            effective_engine_config = await ScanInvoker.__get_logical_engine_config(client, 
                                        repo_config, engine_config, branch)
            if branch is not None:
                effective_branch = branch
            elif await repo_config.primary_branch is not None:
                effective_branch = await repo_config.primary_branch
            else:
                raise ScanException("Branch could not be determined")
        else:
            effective_engine_config = engine_config
            effective_branch = branch

        submit_payload = {
            "project" : {"id" : project_id},
            "type" : "git",
            "config" : effective_engine_config,
            "handler" : {
                "branch" : effective_branch,
                "repoUrl" : clone_url
                }
            }
        
        if clone_user is not None or clone_cred_value is not None:
            submit_payload['handler']['credentials'] = {}

        if clone_user is not None:
            submit_payload['handler']['credentials']['username'] = clone_user

        if clone_cred_value is not None:
            submit_payload['handler']['credentials']['value'] = clone_cred_value
            submit_payload['handler']['credentials']['type'] = clone_cred_type.value

        if scan_tags is not None:
            submit_payload["tags"] = scan_tags

        return await run_a_scan(client, submit_payload)


    @staticmethod
    async def __upload_zip(cxone_client : CxOneClient, zip_path : str, max_retries : int = 5, retry_delay_s : int = 3) -> str:
        _log = logging.getLogger("ScanInvoker.__upload_zip")

        upload_url = None
        retries = 0
        while retries < max_retries:
            if not retries == 0:
                await asyncio.sleep(retry_delay_s)
            retries += 1

            link_response = await generate_upload_link(cxone_client)
            if link_response.ok:
                upload_url = link_response.json()['url']
            else:
                _log.debug(f"Failed to generate link: {link_response.status_code} {link_response.text}")
                continue

            upload_response = await upload_to_link(cxone_client, upload_url, zip_path)
            if not upload_response.ok:
                _log.debug(f"Failed to upload zip: {link_response.status_code} {link_response.text}")
                upload_url = None
                continue
            else:
                break

        if upload_url is None:
            raise ScanException("Failed to upload the zip for scan.")

        return upload_url




class ScanInspector:
    __root_status_query = parse("$.status")
    __scan_engines_query = parse("$.engines")
    __status_details_query = parse("$.statusDetails")

    __projectid_query = parse("$.projectId")
    __scanid_query = parse("$.id")

    __executing_states = ["Queued", "Running"]
    __failed_states = ["Failed", "Canceled"]
    __maybe_states = ["Partial"]
    __success_states = ["Completed"]

    def __init__(self, json : dict):
        """A class used to inspect the status of a scan.

        :param json: A json dictionary of the scan data from the retrieve_scan_details API
        :type json: Dict
        """
        self.__json = json

    def __root_status(self):
        return ScanInspector.__root_status_query.find(self.__json)[0].value

    def __requested_engines(self):
        return ScanInspector.__scan_engines_query.find(self.__json)[0].value

    def __status_details(self):
        details = ScanInspector.__status_details_query.find(self.__json)
        if len(details) > 0:
            return details[0].value
        else:
            return []

    @property
    def project_id(self):
        """The project ID containing the scan."""
        return ScanInspector.__projectid_query.find(self.__json)[0].value

    @property
    def scan_id(self):
        """The scan ID of the scan."""
        return ScanInspector.__scanid_query.find(self.__json)[0].value

    def __current_engine_states(self):
        return_states = []
        engines = self.__requested_engines()
        details = self.__status_details()
        for detail_dict in details:
            if detail_dict['name'] in engines:
                if detail_dict['status'] not in return_states:
                    return_states.append(detail_dict['status'])

        return return_states


    @property
    def json(self) -> dict:
        """The raw scan details json"""
        return self.__json

    @property
    def executing(self) -> bool:
        """Returns a boolean value indicating if the scan is currently executing."""
        if self.__root_status() in ScanInspector.__executing_states:
            return True
        elif self.__root_status() in ScanInspector.__maybe_states:
            return len([s for s in self.__current_engine_states() if s in
                        ScanInspector.__executing_states + ScanInspector.__maybe_states]) > 0

        return False

    @property
    def failed(self):
        """Returns a boolean value indicating if the scan ended in a failed state."""
        if self.__root_status() in ScanInspector.__failed_states:
            return True

        return False

    @property
    def successful(self):
        """Returns a boolean value indicating if the scan ended in a successful state."""
        if self.__root_status() in ScanInspector.__success_states:
            return True
        elif self.executing:
            return False
        elif self.__root_status() in ScanInspector.__maybe_states:
            maybe = [s for s in self.__current_engine_states() if s in ScanInspector.__maybe_states]
            success = [s for s in self.__current_engine_states()
                       if s in ScanInspector.__success_states]
            failed = [s for s in self.__current_engine_states()
                       if s in ScanInspector.__failed_states]
            return len(maybe) == 0 and len(failed) == 0 and len(success) > 0

        return False

    @property
    def state_msg(self):
        """A message about the state of the scan."""
        engine_statuses = []

        for detail in self.__status_details():
            stub = f"{detail['name']}: {detail['status']}"
            if detail['status'] not in ScanInspector.__success_states and \
                len(detail['details']) > 0:
                engine_statuses.append(f"{stub}({detail['details']})")
            else:
                engine_statuses.append(stub)

        return f"Status: {self.__root_status()} [{'|'.join(engine_statuses)}]"


class ScanFilterConfig:
    """A class for computing inherited scan file filters.

    This class produces filters that are combined with the tenant and project
    configuration.  This produces JSON that can be submitted as part of a scan
    request.
    """

    @staticmethod
    async def from_project_config_json(cxone_client : CxOneClient,
        project_config : list, tenant_config : list = None):
        """A static method to produce a filter using the JSON project configuration data.

        :param cxone_client: The CxOneClient instance used to communicate with Checkmarx One.
        :type cxone_client: CxOneClient

        :param project_config: A JSON dictionary returned from the retrieve_project_configuration API.
        :type project_config: list

        :param tenant_config: A JSON dictionary returned from the retrieve_tenant_configuration API.
        :type tenant_config: list, optional

        """
        retval = ScanFilterConfig()

        if tenant_config is None:
            working_tenant_config = json_on_ok(await retrieve_tenant_configuration(cxone_client) )
        else:
            working_tenant_config = tenant_config

        retval.__engine_filters = {}

        ScanFilterConfig.__set_engine_filter(working_tenant_config, retval.__engine_filters)
        ScanFilterConfig.__set_engine_filter(project_config, retval.__engine_filters)

        return retval

    @staticmethod
    def __set_engine_filter(project_config_dict, dest_dict):
        for entry in project_config_dict:
            if entry['value'] is None or len(entry['value']) == 0:
                continue

            if entry['key'].startswith("scan.config"):
                engine_name, config_name = entry['key'].split(".")[-2:]

                if config_name == "filter":
                    if engine_name not in dest_dict.keys():
                        dest_dict[engine_name] = { config_name : entry['value']}
                    else:
                        dest_dict[engine_name][config_name] = ScanFilterConfig.__append_csv_strings(
                            dest_dict[engine_name][config_name], entry['value'])

    @staticmethod
    async def from_project_id(cxone_client : CxOneClient, project_id : str):
        """Creates an instance of ScanFilterConfig with a given project ID
        
        :param cxone_client: The CxOneClient instance used to communicate with Checkmarx One.
        :type cxone_client: CxOneClient

        :param project_id: The project ID that has the filter configuration.
        :type project_id: str
    
        :rtype: ScanFilterConfig
        """
        return await ScanFilterConfig.from_project_config_json(cxone_client,
                        json_on_ok(await retrieve_project_configuration(cxone_client, project_id=project_id)))

    @staticmethod
    async def from_repo_config(cxone_client : CxOneClient, repo_config : ProjectRepoConfig):
        """Creates an instance of ScanFilterConfig using an instance of ProjectRepoConfig
        
        :param cxone_client: The CxOneClient instance used to communicate with Checkmarx One.
        :type cxone_client: CxOneClient

        :param repo_config: An instance of ProjectRepoConfig for a project that has the filter configuration.
        :type repo_config: ProjectRepoConfig
    
        :rtype: ScanFilterConfig
        """
        return await ScanFilterConfig.from_project_config_json(cxone_client, await repo_config.get_project_scan_config())

    @staticmethod
    def __append_csv_strings(left : str, right : str) -> str:
        if left is None:
            return right

        if right is None:
            return left

        return f"{left.rstrip(',')},{right.lstrip(',')}"

    def compute_filters_with_defaults(self, default_engine_config : dict) -> dict:
        """Creates a dictionary with engine file filter configurations based on the tenant, project, and provided file filter criteria
        
        :param default_engine_config: A JSON dictionary with the engine configurations in the format
        used in scan submission JSON requests.
        :type default_engine_config: dict

        :rtype: dict
        """
        retval = {}
        for engine in default_engine_config.keys():
            if engine not in retval.keys():
                retval[engine] = {}

            if default_engine_config[engine] is None:
                continue

            for config_name in default_engine_config[engine].keys():

                if config_name == 'filter' and engine in self.__engine_filters.keys() and \
                    "filter" in self.__engine_filters[engine].keys():
                    retval[engine][config_name] = ScanFilterConfig.__append_csv_strings(
                        self.__engine_filters[engine][config_name],
                        default_engine_config[engine][config_name])
                else:
                    retval[engine][config_name] = default_engine_config[engine][config_name]

        return retval

    @property
    def engines_with_filters(self) -> List[str]:
        """Returns a list of engines with configured file filters."""
        return list(self.__engine_filters.keys())
    
    def compute_filters(self, engine : str, additional_filters : str = None) -> str:
        """Retrieves file filters for the specified engine and also adds additional filters.
        
        :param engine: The name of the engine for the filter.
        :type engine: str

        :param additional_filters: A comma-separated filter string that is additionally added to the
        filters inherited by the tenant and project.
        :type additional_filters: str

        :rtype: str
        """
        ret_val = additional_filters
        if engine in self.__engine_filters.keys():
            if ret_val is None or len(ret_val) == 0:
                ret_val = self.__engine_filters[engine]['filter']
            else:
                ret_val = ScanFilterConfig.__append_csv_strings(ret_val, self.__engine_filters[engine]['filter'])

        return ret_val

class ScanLoader:

    @staticmethod
    async def load(cxone_client : CxOneClient, scanid : str) -> ScanInspector:
        """Creates an instance of ScanInspector for the provided Scan Id

            :param client: The CxOneClient instance used to communicate with Checkmarx One
            :type client: CxOneClient

            :param scanid: The scan id to be inspected.
            :type scanid: str

            :rtype: ScanInspector
            
        """
        scan = json_on_ok(await retrieve_scan_details(cxone_client, scanid))
        return ScanInspector(scan)

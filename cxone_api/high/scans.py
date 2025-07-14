from typing import Union, List
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
import asyncio, logging


class ScanInvoker:
    @staticmethod
    async def scan_get_response(cxone_client : CxOneClient, project_repo : ProjectRepoConfig,
                    branch : str, engine_config : Union[list,dict] = None , tags : dict = None,
                    src_zip_path : str = None, clone_user : str = None,
                    clone_cred_type : str = None, clone_cred_value : str = None) -> Response:

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
            submit_payload["repoOrigin"] = await project_repo.scm_type
            submit_payload["project"] = {
                "repoIdentity" : await project_repo.scm_repo_id,
                "repoUrl" : await project_repo.repo_url,
                "projectId" : project_repo.project_id,
                "defaultBranch" : branch,
                "scannerTypes" : engine_config if engine_config is not None else [],
                "repoId" : await project_repo.repo_id
            }

            scm_org = await project_repo.scm_org

            return await run_a_repo_scan(cxone_client, await project_repo.scm_id,
                        project_repo.project_id,
                        scm_org if scm_org is not None else "anyorg", submit_payload)

    @staticmethod
    async def scan_get_scanid(cxone_client : CxOneClient, project_repo : ProjectRepoConfig,
                              branch : str, engines : list = None , tags : dict = None,
                              src_zip_path : str = None, clone_user : str = None,
                              clone_cred_type : str = None, clone_cred_value : str = None) -> str:

        response = await ScanInvoker.scan_get_response(cxone_client, project_repo, branch, engines,
                              tags, src_zip_path, clone_user, clone_cred_type, clone_cred_value)

        if not response.ok:
            raise ScanException(f"Scan error for project {project_repo.project_id}: "
                                f"Status: {response.status_code} : {response.json()}")

        response_json = response.json()

        return response_json['id'] if "id" in response_json.keys() else None


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
        self.__json = json

    def __root_status(self):
        return ScanInspector.__root_status_query.find(self.__json)[0].value

    def __requested_engines(self):
        return ScanInspector.__scan_engines_query.find(self.__json)[0].value

    def __status_details(self):
        return ScanInspector.__status_details_query.find(self.__json)[0].value

    @property
    def project_id(self):
        return ScanInspector.__projectid_query.find(self.__json)[0].value

    @property
    def scan_id(self):
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
        return self.__json

    @property
    def executing(self):
        if self.__root_status() in ScanInspector.__executing_states:
            return True
        elif self.__root_status() in ScanInspector.__maybe_states:
            return len([s for s in self.__current_engine_states() if s in
                        ScanInspector.__executing_states + ScanInspector.__maybe_states]) > 0

        return False

    @property
    def failed(self):
        if self.__root_status() in ScanInspector.__failed_states:
            return True

        return False

    @property
    def successful(self):
        if self.__root_status() in ScanInspector.__success_states:
            return True
        elif self.executing:
            return False
        elif self.__root_status() in ScanInspector.__maybe_states:
            maybe = [s for s in self.__current_engine_states() if s in ScanInspector.__maybe_states]
            success = [s for s in self.__current_engine_states()
                       if s in ScanInspector.__success_states]
            return len(maybe) == 0 and len(success) > 0

        return False

    @property
    def state_msg(self):
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

    @staticmethod
    async def from_project_config_json(cxone_client : CxOneClient,
        project_config : list, tenant_config : list = None):
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
        return await ScanFilterConfig.from_project_config_json(cxone_client,
                        json_on_ok(await retrieve_project_configuration(cxone_client, project_id)))

    @staticmethod
    async def from_repo_config(cxone_client : CxOneClient, repo_config : ProjectRepoConfig):
        return await ScanFilterConfig.from_project_config_json(cxone_client, await repo_config.get_project_scan_config())

    @staticmethod
    def __append_csv_strings(left : str, right : str) -> str:
        if left is None:
            return right

        if right is None:
            return left

        return f"{left.rstrip(',')},{right.lstrip(',')}"

    def compute_filters_with_defaults(self, default_engine_config : dict) -> dict:
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
        return list(self.__engine_filters.keys())
    
    def compute_filters(self, engine : str, additional_filters : str = None) -> str:
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
        scan = json_on_ok(await retrieve_scan_details(cxone_client, scanid))
        return ScanInspector(scan)

from cxone_api.low.policy_management import retrieve_policy_violation_info, retrieve_all_policies
from cxone_api.high.scans import ScanInspector
from cxone_api import CxOneClient
from cxone_api.util import json_on_ok, page_generator
import asyncio
from typing import List
from dataclasses import dataclass
from jsonpath_ng.ext import parse


class PolicyEvaluationIncomplete(Exception):
  """An exception that indicates when policy evaluation has not completed."""
  def __init__(self, projectid : str, scanid : str):
    """Initializes the exception with a message that can locate the scan where the policy evaluation is not complete.
    """
    super().__init__(f"Policy evaluation is not yet complete for scan id {scanid} in project id {projectid}")


@dataclass(frozen=True)
class PolicyViolationDescriptor:
  """A class that describes policy violations."""
  PolicyName : str
  BreakBuild : bool
  ViolatedRules : List[str]

class PolicyViolationInspector:
  """A class used to inspect policy violations for a scan.

    Create an instance using the static factory methods.
  
  """

  __assigned_projects_query = parse("$.projects[*].astProjectId")

  @staticmethod
  def from_scan_inspector(client : CxOneClient, inspector : ScanInspector):
    """A factory method to create the PolicyViolationInspector instance from a ScanInspector instance.

        :param client: The CxOneClient instance used to communicate with Checkmarx One
        :type client: CxOneClient

        :param inspector: A ScanInspector instance.
        :type inspector: ScanInspector

        :param allow_incomplete_evaluation: A boolean value indicating if incomplete evaluation will be considered the same as complete evaluation.
        :type allow_incomplete_evaluation: bool,optional

        :rtype: PolicyViolationInspector
    """
    return PolicyViolationInspector.from_project_and_scan_ids(client, inspector.project_id, inspector.scan_id)

  @staticmethod
  def from_project_and_scan_ids(client : CxOneClient, projectid : str, scanid : str):
    """A factory method to create the PolicyViolationInspector instance using the project id and scan id.

        :param client: The CxOneClient instance used to communicate with Checkmarx One
        :type client: CxOneClient

        :param projectid: The ID of the project containing the scan.
        :type projectid: str

        :param scanid: The ID of the scan for which policy violations should be inspected.
        :type scanid: str

        :rtype: PolicyViolationInspector
    """
    inst = PolicyViolationInspector()
    inst.__client = client
    inst.__projectid = projectid
    inst.__scanid = scanid
    inst.__lock = asyncio.Lock()
    inst.__violations = None
    inst.__break_build = False
    inst.__has_violations = False
    inst.__initialized = False

    return inst

  @property
  def scanid(self) -> str:
    """The scan id that this instance is inspecting."""
    return self.__scanid
  
  @property
  def projectid(self) -> str:
    """The project id containing the scan that this instance is inspecting."""
    return self.__projectid
  
  async def __load_violations(self):
    async with self.__lock:
      if self.__violations is None and not self.__initialized:
        data = json_on_ok(await retrieve_policy_violation_info(self.__client, self.projectid, self.scanid))

        if data.get("status", "NONE") == "NONE":
          # Two cases can yield NONE:
          # * no policies apply to the project
          # * the policy evaluation has not yet started after the scan
          #
          # If there is a default policy or if any policy has this project assigned, NONE needs to throw an incomplete exception.
          # Otherwise there is no build break since there are no policies to enforce.
          async for single_policy in page_generator(retrieve_all_policies, "policies", "page", offset_init_value=1, offset_is_by_count=False, client=self.__client):
            if single_policy.get("defaultPolicy", False):
              # A default policy exists but it is likely that the policy evaluation has not started.
              raise PolicyEvaluationIncomplete(self.projectid, self.scanid)

            assigned_projects = [x.value for x in PolicyViolationInspector.__assigned_projects_query.find(single_policy)]

            if self.projectid in assigned_projects:
              # This project is assigned to at least one policy so the evaluation must be COMPLETE
              raise PolicyEvaluationIncomplete(self.projectid, self.scanid)

        elif not data.get("status", "") == "COMPLETED":
          raise PolicyEvaluationIncomplete(self.projectid, self.scanid)
        
        self.__break_build = data.get("breakBuild", False)
        policy_array = data.get("policies", None)

        if policy_array is not None and len(policy_array) > 0:
          for evaluated in policy_array:
            if evaluated.get("status", "") == "FAILED":
              self.__has_violations = True
              violation_descriptor = PolicyViolationDescriptor(evaluated['policyName'], evaluated['breakBuild'], evaluated['rulesViolated'])
              if self.__violations is None:
                self.__violations = [violation_descriptor]
              else:
                self.__violations.append(violation_descriptor)
        
        self.__initialized = True
        
  
  @property
  async def break_build(self) -> bool:
    """Indicates if the policy violations are intended to cause a build break.

       :raises PolicyEvaluationIncomplete: An exception is thrown if the policy evaluation has not yet been completed.
    """
    await self.__load_violations()
    return self.__break_build

  @property
  async def has_violations(self) -> bool:
    """Indicates if there are any policies in violation, even if the violated policies are not required to break the build.
    
       :raises PolicyEvaluationIncomplete: An exception is thrown if the policy evaluation has not yet been completed.
    """
    await self.__load_violations()
    return self.__has_violations
  
  @property
  async def policy_violations(self) -> List[PolicyViolationDescriptor]:
    """Retrieves a list of PolicyViolationDescriptor objects that represent the violated policies.
        
       :raises PolicyEvaluationIncomplete: An exception is thrown if the policy evaluation has not yet been completed.
    """
    await self.__load_violations()
    return self.__violations


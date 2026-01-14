from cxone_api.low.policy_management import retrieve_policy_violation_info
from cxone_api.high.scans import ScanInspector
from cxone_api import CxOneClient
from cxone_api.util import json_on_ok
import asyncio
from typing import List
from dataclasses import dataclass


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
  ViolatedPolicies : List[str]


class PolicyViolationInspector:
  """A class used to inspect policy violations for a scan.

    Create an instance using the static factory methods.
  
  """

  @staticmethod
  def from_scan_inspector(client : CxOneClient, inspector : ScanInspector):
    """A factory method to create the PolicyViolationInspector instance from a ScanInspector instance.

        :param client: The CxOneClient instance used to communicate with Checkmarx One
        :type client: CxOneClient

        :param inspector: A ScanInspector instance.
        :type inspector: ScanInspector

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
      if self.__violations is None:
        data = json_on_ok(await retrieve_policy_violation_info(self.__client, self.projectid, self.scanid))
        
        if not data.get("status", "") == "COMPLETED":
          raise PolicyEvaluationIncomplete(self.projectid, self.scanid)
        
        self.__break_build = data.get("breakBuild", False)
        policy_array = data.get("policies", None)

        if policy_array is not None and len(policy_array) > 0:
          for evaluated in policy_array:
            if evaluated.get("status", "") == "FAILED":
              self.__has_violations = True
              violation_descriptor = PolicyViolationDescriptor(evaluated['policyName'], evaluated['rulesViolated'])
              if self.__violations is None:
                self.__violations = [violation_descriptor]
              else:
                self.__violations.append(violation_descriptor)
        
  
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


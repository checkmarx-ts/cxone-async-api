from __future__ import annotations
from ... import CxOneClient
from ...low.misc import retrieve_feature_flags
from ...util import json_on_ok
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from dataclasses_json import LetterCase, config, dataclass_json


@dataclass_json
@dataclass(frozen=True)
class CxOneFlag:
    """A data class describing a single Checkmarx One feature flag."""
    Name: str = field(metadata=config(letter_case=LetterCase.CAMEL))
    """The name of the feature flag."""
    Status: bool = field(metadata=config(letter_case=LetterCase.CAMEL))
    """A boolean value indicating if the feature flag is enabled."""
    Payload: Optional[Dict] = field(metadata=config(letter_case=LetterCase.CAMEL))
    """An optional dictionary containing additional data associated with the feature flag."""


class FeatureFlagInspector:
    """A class used to inspect the state of Checkmarx One feature flags."""

    def __init__(self):
        """Initializes an empty FeatureFlagInspector.

        Instances should be created using the :py:meth:`create` factory method rather
        than invoking the constructor directly.
        """
        self.__name_index = {}
        self.__status_index = {}

    @staticmethod
    async def create(client: CxOneClient) -> FeatureFlagInspector:
        """Creates a FeatureFlagInspector instance populated with the feature flags
        currently reported by Checkmarx One.

        :param client: The CxOneClient instance used to communicate with Checkmarx One
        :type client: CxOneClient

        :rtype: FeatureFlagInspector
        """

        inst = FeatureFlagInspector()

        flags_json = json_on_ok(await retrieve_feature_flags(client))

        for flag_data in flags_json:
            # pylint: disable=E1101
            flag_inst = CxOneFlag.from_dict(flag_data)
            inst.__name_index[flag_inst.Name] = flag_inst

            if flag_inst.Status not in inst.__status_index.keys():
                inst.__status_index[flag_inst.Status] = []

            inst.__status_index[flag_inst.Status].append(flag_inst.Name)

        return inst

    def __getitem__(self, flag_name: str) -> CxOneFlag | None:
        """Retrieves a feature flag by name if it exists, None otherwise.

        :param flag_name: The name of the feature flag to retrieve.
        :type flag_name: str

        :rtype: CxOneFlag | None
        """
        return self.__name_index.get(flag_name)

    @property
    def all(self) -> List[CxOneFlag]:
        """A list of all known feature flags."""
        return list(self.__name_index.values())

    def all_flags_true(self, flags: List[str]) -> bool:
        """Determines if all of the given feature flags have a status of True.

        :param flags: The names of the feature flags to check.
        :type flags: List[str]

        :rtype: bool
        """
        if True not in self.__status_index.keys():
            False

        for flag in flags:
            if flag not in self.__status_index[True]:
                return False

        return True

    def all_flags_False(self, flags: List[str]) -> bool:
        """Determines if all of the given feature flags have a status of False.

        :param flags: The names of the feature flags to check.
        :type flags: List[str]

        :rtype: bool
        """
        if False not in self.__status_index.keys():
            return False

        for flag in flags:
            if flag not in self.__status_index[False]:
                return True

        return False

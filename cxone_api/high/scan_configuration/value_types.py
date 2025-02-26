from enum import Enum
from typing import List


class ScanLanguageMode(Enum):
  PRIMARY = "primary"
  MULTI = "multi"

  def __str__(self):
      return str(self.value)   


class RestListEnum:
   async def get_enum(self) -> List[str]:
      raise NotImplementedError("_get_enum")
   
   async def is_valid(self, value : str) -> bool:
      val_list = await self.get_enum()
      return value in val_list
   

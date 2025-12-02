class NameNotFoundException(Exception):
  @property
  def name(self) -> str:
    return self.__name
  
  def __init__(self, name : str):
    super().__init__(f"Unknown: {name}")
    self.__name = name

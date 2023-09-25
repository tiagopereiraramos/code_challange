import dataclasses
from dataclasses import dataclass, field
import datetime


@dataclass
class Article:
    # Helper to make it easier to pass around selectors and reduce number of args in each function
    title: str = ''
    date: datetime = ''
    description: str = ''
    picture_filename: str = ''
    title_count_phrase: int = 0
    description_count_phrase: int = 0
    find_money_title_description: bool = False
   
    def __str__(self):
        """Returns a string containing only the non-default field values."""
        s = ', '.join(f'{field.name}={getattr(self, field.name)!r}'
                      for field in dataclasses.fields(self)
                      if getattr(self, field.name))
        return f'{type(self).__name__}({s})'

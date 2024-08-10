from dataclasses import dataclass
from datetime import datetime


@dataclass
class SourceResult:
    """
    Дата-класс для результатов сбора информации из источника
    """
    type: str
    title: str
    link: str
    time: datetime
    text: str | None = None
    picture: str | None = None

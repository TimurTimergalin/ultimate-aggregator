from abc import ABC, abstractmethod
from datetime import datetime

from .source_result import SourceResult


class Source(ABC):
    """
    Абстрактный класс источников информации - объектов, собирающие информацию и сжимающие ее в кусочки
    """

    def __init__(self, name, gathering_period):
        self.name = name
        self.gathering_period = gathering_period
        self.last_gathered = datetime.now()

    async def gather_data(self) -> list[SourceResult]:
        results, last_gathered = await self._gather_data()
        self.last_gathered = last_gathered
        return results

    @abstractmethod
    async def _gather_data(self) -> tuple[list[SourceResult], datetime]:
        """
        Ищет новую информацию
        :return: список результатов
        """
        pass

    __default_picture__ = None

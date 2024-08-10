from abc import ABC, abstractmethod
from datetime import datetime

from .source_result import SourceResult


class Source(ABC):
    """
    Абстрактный класс источников информации - объектов, собирающие информацию и сжимающие ее в кусочки
    """
    def __init__(self, name):
        self.name = name

    @abstractmethod
    async def gather_data(self, since: datetime) -> list[SourceResult]:
        """
        Ищет новую информацию
        :param since: самая ранняя дата публикации интересующей информации
        :return: список результатов
        """
        pass

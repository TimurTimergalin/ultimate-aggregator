from typing import Sequence
from abc import ABC, abstractmethod

from sources import Source, SourceResult


class SourceManager(ABC):
    """
    Интерфейс менеджера источников информации - объекта, отвечающего за хранение и запуск источников информации
    """

    @property
    @abstractmethod
    def sources(self) -> dict[int, Source]:
        """
        Словарь: ключи - идентификаторы, значения - источники информации
        :return: словарь источников информации
        """
        pass

    @abstractmethod
    def add_source(self, source: Source, enforced_id: int | None = None) -> int:
        """
        Сохраняет новый источник информации
        :param source: источник информации
        :param enforced_id: идентификатор, который стоит присвоить добавленному ресурсу. Если не указан, менеджер
        выберет его самостоятельно
        :return: идентификатор добавленного источника информации
        """
        pass

    @abstractmethod
    def remove_source(self, source_id: int) -> None:
        """
        Удаляет источник информации
        :param source_id: идентификатор источника информации
        """
        pass

    @abstractmethod
    async def gather_data(self, source_ids: Sequence[int]) -> dict[int, list[SourceResult]]:
        """
        Запускает сбор кусочков информации
        :param source_ids: Идентификаторы интересующих источников
        :return: Словарь результатов: ключ - идентификатор источника, значение - список результатов
        """
        pass

from typing import Protocol, Sequence

from sources import Source, SourceResult


class SourceManager(Protocol):
    """
    Протокол менеджера источников информации - объекта, отвечающего за хранение и запуск источников информации
    """

    def add_source(self, source: Source) -> int:
        """
        Сохраняет новый источник информации
        :param source: источник информации
        :return: идентификатор добавленного источника информации
        """
        pass

    def remove_source(self, source_id: int) -> None:
        """
        Удаляет источник информации
        :param source_id: идентификатор источника информации
        """
        pass

    async def gather_data(self, source_ids: Sequence[int]) -> dict[int, list[SourceResult]]:
        """
        Запускает сбор кусочков информации
        :param source_ids: Идентификаторы интересующих источников
        :return: Словарь результатов: ключ - идентификатор источника, значение - список результатов
        """
        pass

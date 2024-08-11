from asyncio import TaskGroup
from typing import Sequence

import sources as sources_module
from sources import SourceResult


class BasicSourceManager:
    """
    Базовый менеджер источников информации - хранит источники информации в оперативной памяти.
    Назначает собственные идентификаторы источникам.
    Не обладает персистентностью.
    Удовлетворяет протоколу SourceManager.
    """

    def __init__(self):
        self.next_id = 1
        self._sources = {}

    @property
    def sources(self) -> dict[int, sources_module.Source]:
        return self._sources

    def add_source(self, source: sources_module.Source) -> int:
        self.sources[self.next_id] = source
        self.next_id += 1
        return self.next_id - 1

    def remove_source(self, source_id: int) -> None:
        del self.sources[source_id]

    @staticmethod
    async def _launch_source(source: sources_module.Source, source_id: int, res_dict: dict[int, list[SourceResult]]) -> None:
        results = await source.gather_data()
        res_dict[source_id] = results

    async def gather_data(self, source_ids: Sequence[int]) -> dict[int, list[SourceResult]]:
        results: dict[int, list[SourceResult]] = {}

        with TaskGroup() as tg:
            for source_id in source_ids:
                source = self.sources[source_id]
                tg.create_task(self._launch_source(source, source_id, results))

        return results

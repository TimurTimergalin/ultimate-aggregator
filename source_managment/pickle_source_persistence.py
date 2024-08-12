from pickle import dump, load, UnpicklingError
from typing import Sequence
from weakref import finalize

import sources as sources_module
from sources import SourceResult
from .basic_source_manager import BasicSourceManager
from .source_manager import SourceManager


class PickleSourcePersistence(SourceManager):
    """
    Надстройка над BasicSourceManager, использующая pickle для персистентности.
    Удовлетворяет протоколу SourceManager.
    """

    def __init__(self, path_to_save_file: str):
        self.path_to_save_file = path_to_save_file
        self.source_manager = self.acquire_source_manager()
        finalize(self, self.finalize)

    def acquire_source_manager(self) -> BasicSourceManager:
        try:
            with open(self.path_to_save_file, "rb") as f:
                obj = load(f)
        except UnpicklingError:
            obj = BasicSourceManager()

        return obj

    @property
    def sources(self) -> dict[int, sources_module.Source]:
        return self.source_manager.sources

    def add_source(self, source: sources_module.Source) -> int:
        return self.source_manager.add_source(source)

    def remove_source(self, source_id: int) -> None:
        return self.source_manager.remove_source(source_id)

    async def gather_data(self, source_ids: Sequence[int]) -> dict[int, list[SourceResult]]:
        return await self.source_manager.gather_data(source_ids)

    def finalize(self):
        with open(self.path_to_save_file, "wb") as f:
            dump(self.source_manager, f)

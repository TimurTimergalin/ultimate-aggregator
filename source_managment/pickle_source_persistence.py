from datetime import datetime
from pickle import dump, load, UnpicklingError
from weakref import finalize

import sources
from sources import SourceResult
from .basic_source_manager import BasicSourceManager


class PickleSourcePersistence:
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

    def add_source(self, source: sources.Source) -> int:
        return self.source_manager.add_source(source)

    def remove_source(self, source_id: int) -> None:
        return self.source_manager.remove_source(source_id)

    async def gather_data(self, since: datetime) -> dict[int, list[SourceResult]]:
        return await self.source_manager.gather_data(since)

    def finalize(self):
        with open(self.path_to_save_file, "wb") as f:
            dump(self.source_manager, f)

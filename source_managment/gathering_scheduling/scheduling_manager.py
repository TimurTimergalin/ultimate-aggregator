from typing import Sequence

from ..source_manager import SourceManager
from .scheduler import Scheduler
from sources import Source, SourceResult


class SchedulingManager:
    def __init__(self, source_manager: SourceManager):
        self.source_manager = source_manager
        self.scheduler = Scheduler(source_manager)

    @property
    def sources(self) -> dict[int, Source]:
        return self.source_manager.sources

    def add_source(self, source: Source):
        sid = self.source_manager.add_source(source)
        self.scheduler.schedule_gathering(sid, source)
        return sid

    def remove_source(self, source_id: int):
        self.source_manager.remove_source(source_id)
        self.scheduler.cancel_gathering(source_id)

    async def gather_data(self, source_ids: Sequence[int]) -> dict[int, list[SourceResult]]:
        return await self.source_manager.gather_data(source_ids)

import asyncio

from sources import Source
from ..source_manager import SourceManager


class Scheduler:
    def __init__(self, source_manager: SourceManager):
        self.scheduled_tasks = {}
        self.source_manager = source_manager

        for source_id, source in source_manager.sources:
            self.schedule_gathering(source_id, source)

    async def periodic_gathering(self, source_id: int, gathering_period: int):
        while True:
            await asyncio.sleep(gathering_period)
            await self.source_manager.gather_data([source_id])

    def schedule_gathering(self, source_id: int, source: Source):
        t = asyncio.create_task(self.periodic_gathering(source_id, source.gathering_period))
        self.scheduled_tasks[source_id] = t

    def cancel_gathering(self, source_id: int):
        t = self.scheduled_tasks[source_id]
        t.cancel()
        del self.scheduled_tasks[source_id]

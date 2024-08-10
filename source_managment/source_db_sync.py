from datetime import datetime

from db import DataBase
from db.models import Piece
from sources import SourceResult
from .source_manager import SourceManager
import sources
from db import models

from sqlalchemy import select


class SourceDbSync:
    """
    Декоратор для произвольного SourceManager-а, синхронизирующая его работу с sql базой данных.
    Удовлетворяет протоколу SourceManager.
    """
    def __init__(self, db: DataBase, source_manager: SourceManager):
        self.db = db
        self.source_manager = source_manager

    def add_source(self, source: sources.Source) -> int:
        external_id = self.source_manager.add_source(source)

        with self.db.session() as session:
            to_add = models.Source(external_id=external_id)
            session.add(to_add)

        return to_add.id

    def remove_source(self, db_source_id: int) -> None:
        with self.db.session() as session:
            db_source = session.execute(
                select(models.Source).where(models.Source.id == db_source_id)
            ).first()
            external_id = db_source.external_id
            db_source.delete()

        self.source_manager.remove_source(external_id)

    def save_data(self, data_dict: dict[int, list[SourceResult]]) -> None:
        with self.db.session() as session:
            for source_id, results in data_dict.items():
                db_source = session.execute(
                    select(models.Source).where(models.Source.external_id == source_id)
                ).first()
                for result in results:
                    piece = Piece(
                        type=result.type,
                        title=result.title,
                        text=result.text,
                        picture=result.picture,
                        link=result.link,
                        time=result.time,
                        source=db_source
                    )
                    session.add(piece)

    async def gather_data(self, since: datetime) -> dict[int, list[SourceResult]]:
        results = await self.source_manager.gather_data(since)
        self.save_data(results)
        return results

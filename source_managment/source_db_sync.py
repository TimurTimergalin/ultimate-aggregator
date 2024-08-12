from typing import Sequence

from sqlalchemy import select

import sources as sources_module
from db import DataBase, Session
from db import models
from db.models import Piece
from sources import SourceResult
from .source_manager import SourceManager


class SourceDbSync(SourceManager):
    """
    Декоратор для произвольного SourceManager-а, синхронизирующая его работу с sql базой данных.
    Сохраняет все необходимое в базу данных; подменяет идентификаторы источников информации
    обернутого менеджера идентификаторами из базы данных (на выходе) и наоборот (на входе).
    Удовлетворяет протоколу SourceManager.
    """

    def __init__(self, db: DataBase, source_manager: SourceManager):
        self.db = db
        self.source_manager = source_manager

    @property
    def sources(self) -> dict[int, sources_module.Source]:
        return self.source_manager.sources

    def add_source(self, source: sources_module.Source, enforced_id: int | None = None) -> int:
        assert enforced_id is None

        with self.db.session() as session:
            to_add = models.Source()
            session.add(to_add)
            session.commit()

        self.source_manager.add_source(source, to_add.id)

        return to_add.id

    def remove_source(self, db_source_id: int) -> None:
        with self.db.session() as session:
            db_source, = session.execute(
                select(models.Source).where(models.Source.id == db_source_id)
            ).first()
            db_source.delete()
            session.commit()

        self.source_manager.remove_source(db_source_id)

    @staticmethod
    def save_result(db_source: models.Source, result: SourceResult, session: Session):
        session.add(
            Piece(
                type=result.type,
                title=result.title,
                text=result.text,
                picture=result.picture,
                link=result.link,
                time=result.time,
                source=db_source
            )
        )

    async def gather_data(self, source_ids: Sequence[int]) -> dict[int, list[SourceResult]]:
        results = await self.source_manager.gather_data(source_ids)
        with self.db.session() as session:
            for source_id, results_list in results:
                db_source, = session.execute(
                    select(models.Source).where(models.Source.id == source_id)
                ).first()
                for result in results_list:
                    self.save_result(db_source, result, session)
            session.commit()

        return results

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
        inner_result = self.source_manager.sources
        result = {}
        with self.db.session() as session:
            for external_id, source in inner_result.items():
                db_source = session.execute(
                    select(models.Source).where(models.Source.external_id == external_id)
                ).one()
                result[db_source.id] = source

        return result

    def add_source(self, source: sources_module.Source) -> int:
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
        with self.db.session() as session:
            external_id_to_db_source = {}
            for source_id in source_ids:
                db_source = session.execute(
                    select(models.Source).where(models.Source.id == source_id)
                ).first()
                external_id = db_source.external_id
                external_id_to_db_source[external_id] = db_source

            inner_results = await self.source_manager.gather_data(list(external_id_to_db_source.keys()))
            results = {}
            for external_id, result_list in inner_results.items():
                for result in result_list:
                    self.save_result(external_id_to_db_source[external_id], result, session)
                results[external_id_to_db_source[external_id].id] = result_list

            return results

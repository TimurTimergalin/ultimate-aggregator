from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from .base import Base
from . import category
from . import piece


class Source(Base):
    """
    Источник информации. Извлекает кусочки информации для пользователя.
    Так как источники могут иметь произвольную структуру, хранение информации о них возлагается на другую базу данных.
    Эта модель служит лишь отображением во внешнюю базу данных.
    """
    __tablename__ = "source"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[int] = mapped_column(unique=True, index=True)

    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))
    category: Mapped["category.Category"] = relationship(back_populates="sources")

    pieces: Mapped["piece.Piece"] = relationship(back_populates="source")

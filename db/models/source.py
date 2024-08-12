from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import category
from . import piece
from .base import Base


class Source(Base):
    """
    Источник информации. Извлекает кусочки информации для пользователя.
    Так как источники могут иметь произвольную структуру, хранение информации о них возлагается на другую базу данных.
    Эта модель служит лишь отображением во внешнюю базу данных.
    """
    __tablename__ = "source"

    id: Mapped[int] = mapped_column(primary_key=True)

    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))
    category: Mapped["category.Category"] = relationship(back_populates="sources")

    pieces: Mapped["piece.Piece"] = relationship(back_populates="source")

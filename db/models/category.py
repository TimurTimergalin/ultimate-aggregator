from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from .base import Base
from . import source


class Category(Base):
    """
    Объект категории. Пользователь может распределить различные источники информации по категориям

    Имеет следующие поля:
    - name - имя источника
    """
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True)
    sources: Mapped[list["source.Source"]] = relationship(back_populates="category")

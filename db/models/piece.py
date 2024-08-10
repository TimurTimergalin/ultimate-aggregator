from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text
from datetime import datetime

from .base import Base
from . import source


class Piece(Base):
    """
    Основной объект приложения. "Кусочек" информации - сжатое представление какой-либо информации в интернете:
    статьи, видео, сообщения, поста, блога и т.п.
    Имеет следующие поля:
    - type - тип информации (статья, видео, ...) - строка
    - title - заголовок
    - link - ссылка на оригинал
    - time - время публикации
    - text - описание представляемой информации (опционально)
    - picture - картинка (опционально)
    - source_id - источник информации
    """
    __tablename__ = "piece"
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(128))
    title: Mapped[str] = mapped_column(String(256))
    text: Mapped[str | None] = mapped_column(Text)
    picture: Mapped[str | None] = mapped_column(String(256))
    link: Mapped[str] = mapped_column(String(512))
    time: Mapped[datetime] = mapped_column()

    source_id: Mapped[int] = mapped_column(ForeignKey("source.id"))
    source: Mapped["source.Source"] = relationship(back_populates="pieces")

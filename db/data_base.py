from sqlalchemy import Engine
from sqlalchemy.orm import Session

from db.models import Base


class DataBase:
    """Класс для инициализации базы данных и доступа к ней"""
    def __init__(self, engine: Engine):
        self.engine = engine
        Base.metadata.create_all(engine)

    def session(self) -> Session:
        return Session(self.engine)

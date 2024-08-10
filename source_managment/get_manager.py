from db import DataBase
from .source_manager import SourceManager
from .pickle_source_persistence import PickleSourcePersistence
from .source_db_sync import SourceDbSync


def get_source_manager(*, path_to_save_file: str, db: DataBase) -> SourceManager:
    """
    Фабрика менеджеров источников информации
    :param path_to_save_file: файл для pickle-персистентности
    :param db: объект управления sql базой данных
    :return: сконструированный менеджер
    """
    return SourceDbSync(
        db,
        PickleSourcePersistence(path_to_save_file)
    )

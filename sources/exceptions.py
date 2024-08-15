class SourceException(Exception):
    """Базовое исключение модуля sources."""


class SourceInitException(SourceException):
    """
    Исключение, срабатывающее при попытке инициализировать источник информации невалидными данными.
    """


class SourceGatherException(SourceException):
    """
    Исключение, сигнализирующее об ошибке при сборе информации из источника.
    """

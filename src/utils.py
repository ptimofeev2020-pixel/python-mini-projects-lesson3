"""Модуль utils — утилиты для чтения данных о транзакциях."""

import json
import logging
import os
from typing import Any
from typing import Dict
from typing import List

# ---------------------------------------------------------------------------
# Настройка логера модуля utils
# ---------------------------------------------------------------------------
logger = logging.getLogger("utils")
logger.setLevel(logging.DEBUG)

_log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(_log_dir, exist_ok=True)

_file_handler = logging.FileHandler(os.path.join(_log_dir, "utils.log"), mode="w", encoding="utf-8")
_file_handler.setLevel(logging.DEBUG)

_file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_file_handler.setFormatter(_file_formatter)

logger.addHandler(_file_handler)


def read_transactions_json(path: str) -> List[Dict[str, Any]]:
    """Читает JSON-файл и возвращает список транзакций.

    Принимает путь к JSON-файлу с данными о финансовых транзакциях.
    Если файл не найден, пустой, содержит невалидный JSON или
    данные не являются списком — возвращает пустой список.

    Args:
        path: Путь к JSON-файлу.

    Returns:
        Список словарей с данными о транзакциях.
        Пустой список при любой ошибке чтения или парсинга.

    Example:
        >>> read_transactions_json("data/operations.json")  # doctest: +SKIP
        [{'id': 441945886, 'state': 'EXECUTED', ...}, ...]
        >>> read_transactions_json("nonexistent.json")
        []
    """
    logger.info("Открытие файла: %s", path)
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as exc:
        logger.error("Ошибка чтения файла '%s': %s", path, exc)
        return []

    if not isinstance(data, list):
        logger.error("Данные в файле '%s' не являются списком (тип: %s)", path, type(data).__name__)
        return []

    logger.info("Успешно загружено %d транзакций из файла '%s'", len(data), path)
    return data

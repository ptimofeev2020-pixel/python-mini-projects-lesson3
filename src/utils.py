"""Модуль utils — утилиты для чтения данных о транзакциях."""

import json
from typing import Any
from typing import Dict
from typing import List


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
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []

    if not isinstance(data, list):
        return []

    return data

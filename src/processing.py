"""
Модуль для обработки банковских операций.
Содержит функции для фильтрации и сортировки операций по различным критериям.
"""

import re
from collections import Counter
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List


def filter_by_state(operations: List[Dict[str, Any]], state: str = "EXECUTED") -> List[Dict[str, Any]]:
    """
    Фильтрует список банковских операций по заданному статусу (state).

    :param operations: Список операций, где каждая операция представлена словарём.
                       Пример элемента списка:
                       {
                           "id": 41428829,
                           "state": "EXECUTED",
                           "date": "2019-07-03T18:35:29.512364"
                       }
    :param state: Статус, по которому нужно отфильтровать (по умолчанию "EXECUTED").
    :return: Новый список операций, содержащий только те, у которых "state" совпадает со значением, переданным в функцию.
    """
    return [op for op in operations if op.get("state") == state]


def sort_by_date(operations: List[Dict[str, Any]], descending: bool = True) -> List[Dict[str, Any]]:
    """
    Сортирует список банковских операций по дате (ключ "date").

    :param operations: Список операций, где каждая операция представлена словарём.
                       Ожидается, что значение ключа "date" — строка в формате
                       "YYYY-MM-DDTHH:MM:SS.ffffff", например "2019-07-03T18:35:29.512364".
    :param descending: Порядок сортировки. True = по убыванию (самые последние даты в начале),
                       False = по возрастанию. По умолчанию True.
    :return: Новый список, отсортированный по ключу "date" в заданном порядке.
    """
    # Для совместимости со всеми версиями Python используем strptime с явным
    # форматом. datetime.fromisoformat() в Python < 3.11 может не распознавать
    # некоторые ISO-строки, что приводит к ошибкам разбора.
    date_format = "%Y-%m-%dT%H:%M:%S.%f"

    def _parse_date(op: Dict[str, Any]) -> datetime:
        return datetime.strptime(op["date"], date_format)

    return sorted(operations, key=_parse_date, reverse=descending)


def process_bank_search(data: List[Dict[str, Any]], search: str) -> List[Dict[str, Any]]:
    """Ищет транзакции, в описании которых встречается заданная строка.

    Поиск выполняется по полю ``description`` с использованием
    регулярных выражений (``re``). Поиск регистронезависимый.

    Args:
        data: Список словарей-транзакций.
        search: Строка поиска (подстрока или регулярное выражение).

    Returns:
        Список транзакций, описание которых содержит совпадение.

    Example:
        >>> ops = [
        ...     {"description": "Перевод организации"},
        ...     {"description": "Открытие вклада"},
        ... ]
        >>> process_bank_search(ops, "перевод")
        [{'description': 'Перевод организации'}]
    """
    pattern = re.compile(search, re.IGNORECASE)
    return [op for op in data if pattern.search(op.get("description", ""))]


def process_bank_operations(data: List[Dict[str, Any]], categories: List[str]) -> Dict[str, int]:
    """Подсчитывает количество операций по категориям.

    Категории определяются по значению поля ``description``.
    Используется ``Counter`` из модуля ``collections``.

    Args:
        data: Список словарей-транзакций.
        categories: Список названий категорий для подсчёта.

    Returns:
        Словарь, где ключи — названия категорий,
        значения — количество операций в каждой категории.
        Категории, не встречающиеся в данных, получают значение 0.

    Example:
        >>> ops = [
        ...     {"description": "Перевод организации"},
        ...     {"description": "Перевод организации"},
        ...     {"description": "Открытие вклада"},
        ... ]
        >>> process_bank_operations(ops, ["Перевод организации", "Открытие вклада"])
        {'Перевод организации': 2, 'Открытие вклада': 1}
    """
    counter: Counter[str] = Counter(op.get("description", "") for op in data)
    return {cat: counter.get(cat, 0) for cat in categories}

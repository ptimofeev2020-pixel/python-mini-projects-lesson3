"""
Модуль для обработки банковских операций.
Содержит функции для фильтрации и сортировки операций по различным критериям.
"""

from typing import List, Dict, Any
from datetime import datetime


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
    :param descending: Порядок сортировки. True = по убыванию (самые последние даты в начале),
                       False = по возрастанию. По умолчанию True.
    :return: Новый список, отсортированный по ключу "date" в заданном порядке.
    """
    # Чтобы корректно сортировать по дате, конвертируем строку в datetime
    # и используем её при сортировке.
    def get_date(op: Dict[str, Any]) -> datetime:
        return datetime.fromisoformat(op["date"])

    return sorted(operations, key=get_date, reverse=descending)

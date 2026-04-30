"""Главный модуль проекта — интерактивная работа с банковскими транзакциями."""

import math
from typing import Any
from typing import Dict
from typing import List

from src.processing import filter_by_state
from src.processing import process_bank_search
from src.processing import sort_by_date
from src.readers import read_transactions_csv
from src.readers import read_transactions_xlsx
from src.utils import read_transactions_json
from src.widget import get_date
from src.widget import mask_account_card

VALID_STATUSES = ("EXECUTED", "CANCELED", "PENDING")


def _get_amount(txn: Dict[str, Any]) -> str:
    """Извлекает сумму из транзакции (JSON или CSV/XLSX формат)."""
    if "operationAmount" in txn:
        return str(txn["operationAmount"]["amount"])
    return str(txn.get("amount", "0"))


def _get_currency_code(txn: Dict[str, Any]) -> str:
    """Извлекает код валюты из транзакции (JSON или CSV/XLSX формат)."""
    if "operationAmount" in txn:
        return str(txn["operationAmount"]["currency"]["code"])
    return str(txn.get("currency_code", ""))


def _get_currency_display(txn: Dict[str, Any]) -> str:
    """Возвращает отображаемое название валюты."""
    code = _get_currency_code(txn)
    if code == "RUB":
        return "руб."
    return code


def _format_date(txn: Dict[str, Any]) -> str:
    """Форматирует дату транзакции в ДД.ММ.ГГГГ."""
    date_str = str(txn.get("date", ""))
    if date_str.endswith("Z"):
        date_str = date_str[:-1]
    # Дополняем дату микросекундами, если их нет
    if "." not in date_str and "T" in date_str:
        date_str += ".000000"
    return get_date(date_str)


def _is_empty(value: Any) -> bool:
    """Проверяет, является ли значение пустым (None, NaN, пустая строка)."""
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def _print_transaction(txn: Dict[str, Any]) -> None:
    """Выводит одну транзакцию в формате задания."""
    date = _format_date(txn)
    description = txn.get("description", "")
    print(f"\n{date} {description}")

    from_field = txn.get("from")
    to_field = txn.get("to")

    if not _is_empty(from_field) and not _is_empty(to_field):
        print(f"{mask_account_card(str(from_field))} -> {mask_account_card(str(to_field))}")
    elif not _is_empty(to_field):
        print(mask_account_card(str(to_field)))
    elif not _is_empty(from_field):
        print(mask_account_card(str(from_field)))

    amount = _get_amount(txn)
    currency = _get_currency_display(txn)
    print(f"Сумма: {amount} {currency}")


def _ask_yes_no(prompt: str) -> bool:
    """Спрашивает да/нет у пользователя."""
    answer = input(prompt).strip().lower()
    return answer in ("да", "yes", "y", "д")


def _filter_rub_only(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Фильтрует только рублёвые транзакции."""
    return [txn for txn in transactions if _get_currency_code(txn) == "RUB"]


def _normalize_dates(transactions: List[Dict[str, Any]]) -> None:
    """Нормализует даты CSV/XLSX для совместимости с sort_by_date."""
    for txn in transactions:
        date_str = str(txn.get("date", ""))
        if date_str.endswith("Z"):
            txn["date"] = date_str[:-1] + ".000000"
        elif "T" in date_str and "." not in date_str:
            txn["date"] = date_str + ".000000"


def _choose_source() -> List[Dict[str, Any]]:
    """Запрашивает у пользователя источник данных и загружает транзакции."""
    print("Привет! Добро пожаловать в программу работы с банковскими транзакциями.")
    print("Выберите необходимый пункт меню:")
    print("1. Получить информацию о транзакциях из JSON-файла")
    print("2. Получить информацию о транзакциях из CSV-файла")
    print("3. Получить информацию о транзакциях из XLSX-файла")

    loaders: Dict[str, tuple[str, str]] = {
        "1": ("JSON", "data/operations.json"),
        "2": ("CSV", "data/transactions.csv"),
        "3": ("XLSX", "data/transactions_excel.xlsx"),
    }
    readers = {
        "1": read_transactions_json,
        "2": read_transactions_csv,
        "3": read_transactions_xlsx,
    }

    while True:
        choice = input("\nПользователь: ").strip()
        if choice in loaders:
            name, path = loaders[choice]
            transactions: List[Dict[str, Any]] = readers[choice](path)
            print(f"\nДля обработки выбран {name}-файл.")
            return transactions
        print("Некорректный ввод. Пожалуйста, выберите 1, 2 или 3.")


def _choose_status(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Запрашивает статус фильтрации и применяет фильтр."""
    while True:
        print("\nВведите статус, по которому необходимо выполнить фильтрацию.")
        print("Доступные для фильтровки статусы: EXECUTED, CANCELED, PENDING")
        status_input = input("\nПользователь: ").strip().upper()
        if status_input in VALID_STATUSES:
            filtered = filter_by_state(transactions, status_input)
            print(f'\nОперации отфильтрованы по статусу "{status_input}"')
            return filtered
        print(f'\nСтатус операции "{status_input}" недоступен.')


def _apply_filters(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Применяет опциональные фильтры: сортировка, валюта, поиск."""
    # Сортировка по дате
    if _ask_yes_no("\nОтсортировать операции по дате? Да/Нет\n\nПользователь: "):
        sort_input = input(
            "\nОтсортировать по возрастанию или по убыванию?\n\nПользователь: "
        ).strip().lower()
        descending = sort_input != "по возрастанию"
        _normalize_dates(transactions)
        transactions = sort_by_date(transactions, descending=descending)

    # Фильтрация только рублёвые
    if _ask_yes_no("\nВыводить только рублевые транзакции? Да/Нет\n\nПользователь: "):
        transactions = _filter_rub_only(transactions)

    # Поиск по описанию
    if _ask_yes_no(
        "\nОтфильтровать список транзакций по определенному слову в описании? Да/Нет\n\nПользователь: "
    ):
        search_query = input("\nВведите строку для поиска:\n\nПользователь: ").strip()
        transactions = process_bank_search(transactions, search_query)

    return transactions


def _print_results(transactions: List[Dict[str, Any]]) -> None:
    """Выводит итоговый список транзакций."""
    print("\nРаспечатываю итоговый список транзакций...\n")
    if not transactions:
        print("Не найдено ни одной транзакции, подходящей под ваши условия фильтрации")
    else:
        print(f"Всего банковских операций в выборке: {len(transactions)}")
        for txn in transactions:
            _print_transaction(txn)


def main() -> None:
    """Основная функция программы — интерактивный интерфейс."""
    transactions = _choose_source()
    transactions = _choose_status(transactions)
    transactions = _apply_filters(transactions)
    _print_results(transactions)


if __name__ == "__main__":
    main()

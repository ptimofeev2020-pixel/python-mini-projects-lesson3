"""Модуль generators — генераторы для обработки банковских транзакций."""

from typing import Any
from typing import Dict
from typing import Generator
from typing import Iterator
from typing import List


def filter_by_currency(
    transactions: List[Dict[str, Any]],
    currency: str,
) -> Iterator[Dict[str, Any]]:
    """Фильтрует транзакции по коду валюты операции.

    Возвращает итератор, который поочерёдно выдаёт транзакции,
    где код валюты в ``operationAmount → currency → code`` совпадает
    с переданным значением.

    Args:
        transactions: Список словарей-транзакций. Каждая транзакция содержит
            ключ ``operationAmount`` с вложенной структурой ``currency.code``.
        currency: Код валюты для фильтрации (например, ``"USD"``, ``"RUB"``).

    Yields:
        Словарь-транзакцию, валюта которой совпадает с *currency*.

    Example:
        >>> txns = [
        ...     {"id": 1, "operationAmount": {"amount": "100", "currency": {"code": "USD"}}},
        ...     {"id": 2, "operationAmount": {"amount": "200", "currency": {"code": "RUB"}}},
        ... ]
        >>> usd = filter_by_currency(txns, "USD")
        >>> next(usd)["id"]
        1
    """
    for transaction in transactions:
        if transaction.get("operationAmount", {}).get("currency", {}).get("code") == currency:
            yield transaction


def transaction_descriptions(
    transactions: List[Dict[str, Any]],
) -> Generator[str, None, None]:
    """Генератор описаний банковских транзакций.

    Поочерёдно возвращает значение ключа ``"description"`` для каждой
    транзакции из переданного списка.

    Args:
        transactions: Список словарей-транзакций, каждый из которых
            содержит ключ ``"description"``.

    Yields:
        Строку-описание очередной транзакции.

    Example:
        >>> txns = [{"description": "Перевод организации"}, {"description": "Перевод со счета на счет"}]
        >>> gen = transaction_descriptions(txns)
        >>> next(gen)
        'Перевод организации'
    """
    for transaction in transactions:
        yield transaction["description"]


def card_number_generator(start: int, end: int) -> Generator[str, None, None]:
    """Генератор номеров банковских карт в заданном диапазоне.

    Выдаёт номера карт в формате ``XXXX XXXX XXXX XXXX``, где каждый
    номер — это число от *start* до *end* включительно, дополненное
    ведущими нулями до 16 цифр.

    Args:
        start: Начальное значение диапазона (включительно, ≥ 1).
        end: Конечное значение диапазона (включительно, ≤ 9999999999999999).

    Yields:
        Строку с номером карты в формате ``XXXX XXXX XXXX XXXX``.

    Example:
        >>> gen = card_number_generator(1, 3)
        >>> next(gen)
        '0000 0000 0000 0001'
        >>> next(gen)
        '0000 0000 0000 0002'
    """
    for number in range(start, end + 1):
        digits = str(number).zfill(16)
        yield f"{digits[:4]} {digits[4:8]} {digits[8:12]} {digits[12:]}"

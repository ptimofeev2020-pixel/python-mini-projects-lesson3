"""Модуль external_api — конвертация валют через внешний API."""

import os
from typing import Any
from typing import Dict

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("EXCHANGE_RATES_API_KEY", "")
API_URL = "https://api.apilayer.com/exchangerates_data/convert"


def convert_to_rub(transaction: Dict[str, Any]) -> float:
    """Конвертирует сумму транзакции в рубли.

    Если валюта транзакции — RUB, возвращает сумму как есть.
    Если USD или EUR — обращается к Exchange Rates Data API
    для получения текущего курса и конвертации.

    Args:
        transaction: Словарь-транзакция с ключом ``operationAmount``,
            содержащим ``amount`` (строка) и ``currency.code``.

    Returns:
        Сумма транзакции в рублях (``float``).

    Raises:
        ValueError: Если код валюты не поддерживается.
        requests.RequestException: Если запрос к API завершился ошибкой.

    Example:
        >>> txn = {
        ...     "operationAmount": {
        ...         "amount": "100.00",
        ...         "currency": {"code": "RUB"}
        ...     }
        ... }
        >>> convert_to_rub(txn)
        100.0
    """
    amount_str = transaction["operationAmount"]["amount"]
    currency_code = transaction["operationAmount"]["currency"]["code"]
    amount = float(amount_str)

    if currency_code == "RUB":
        return amount

    if currency_code not in ("USD", "EUR"):
        raise ValueError(f"Неподдерживаемая валюта: {currency_code}")

    response = requests.get(
        API_URL,
        headers={"apikey": API_KEY},
        params={
            "from": currency_code,
            "to": "RUB",
            "amount": amount,
        },
        timeout=10,
    )
    response.raise_for_status()

    data = response.json()
    result: float = float(data["result"])
    return result

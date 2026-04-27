"""Модуль readers — чтение финансовых операций из CSV- и Excel-файлов."""

import logging
import os
from typing import Any
from typing import Dict
from typing import List

import pandas as pd

# ---------------------------------------------------------------------------
# Настройка логера модуля readers
# ---------------------------------------------------------------------------
logger = logging.getLogger("readers")
logger.setLevel(logging.DEBUG)

_log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(_log_dir, exist_ok=True)

_file_handler = logging.FileHandler(os.path.join(_log_dir, "readers.log"), mode="w", encoding="utf-8")
_file_handler.setLevel(logging.DEBUG)

_file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_file_handler.setFormatter(_file_formatter)

logger.addHandler(_file_handler)


def read_transactions_csv(path: str) -> List[Dict[str, Any]]:
    """Читает CSV-файл и возвращает список транзакций.

    Принимает путь к CSV-файлу с данными о финансовых транзакциях.
    Ожидаемый разделитель — точка с запятой (``;``).
    Если файл не найден, пустой или содержит ошибки — возвращает пустой список.

    Args:
        path: Путь к CSV-файлу.

    Returns:
        Список словарей с данными о транзакциях.
        Пустой список при любой ошибке чтения.

    Example:
        >>> read_transactions_csv("data/transactions.csv")  # doctest: +SKIP
        [{'id': 650703, 'state': 'EXECUTED', ...}, ...]
    """
    logger.info("Открытие CSV-файла: %s", path)
    try:
        df = pd.read_csv(path, sep=";")
    except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError, OSError) as exc:
        logger.error("Ошибка чтения CSV-файла '%s': %s", path, exc)
        return []

    transactions: List[Dict[str, Any]] = df.to_dict(orient="records")
    logger.info("Успешно загружено %d транзакций из CSV-файла '%s'", len(transactions), path)
    return transactions


def read_transactions_xlsx(path: str) -> List[Dict[str, Any]]:
    """Читает Excel-файл (.xlsx) и возвращает список транзакций.

    Принимает путь к Excel-файлу с данными о финансовых транзакциях.
    Если файл не найден, пустой или содержит ошибки — возвращает пустой список.

    Args:
        path: Путь к Excel-файлу (.xlsx).

    Returns:
        Список словарей с данными о транзакциях.
        Пустой список при любой ошибке чтения.

    Example:
        >>> read_transactions_xlsx("data/transactions_excel.xlsx")  # doctest: +SKIP
        [{'id': 650703, 'state': 'EXECUTED', ...}, ...]
    """
    logger.info("Открытие Excel-файла: %s", path)
    try:
        df = pd.read_excel(path)
    except (FileNotFoundError, ValueError, OSError) as exc:
        logger.error("Ошибка чтения Excel-файла '%s': %s", path, exc)
        return []

    transactions: List[Dict[str, Any]] = df.to_dict(orient="records")
    logger.info("Успешно загружено %d транзакций из Excel-файла '%s'", len(transactions), path)
    return transactions

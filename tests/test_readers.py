"""Тесты для модуля src.readers — чтение транзакций из CSV и Excel."""

from typing import Any
from typing import Dict
from typing import List
from unittest.mock import MagicMock
from unittest.mock import patch

import pandas as pd
import pytest

from src.readers import read_transactions_csv
from src.readers import read_transactions_xlsx

# ---------------------------------------------------------------------------
# Фикстуры
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Пример DataFrame с транзакциями."""
    return pd.DataFrame(
        {
            "id": [650703, 3598919],
            "state": ["EXECUTED", "EXECUTED"],
            "date": ["2023-09-05T11:30:32Z", "2020-12-06T23:00:58Z"],
            "amount": [16210, 29740],
            "currency_name": ["Sol", "Peso"],
            "currency_code": ["PEN", "COP"],
            "from": ["Счет 58803664561298323391", "Discover 3172601889670065"],
            "to": ["Счет 39745660563456619397", "Discover 0720428384694643"],
            "description": ["Перевод организации", "Перевод с карты на карту"],
        }
    )


@pytest.fixture
def sample_records() -> List[Dict[str, Any]]:
    """Ожидаемые словари из sample_df."""
    return [
        {
            "id": 650703,
            "state": "EXECUTED",
            "date": "2023-09-05T11:30:32Z",
            "amount": 16210,
            "currency_name": "Sol",
            "currency_code": "PEN",
            "from": "Счет 58803664561298323391",
            "to": "Счет 39745660563456619397",
            "description": "Перевод организации",
        },
        {
            "id": 3598919,
            "state": "EXECUTED",
            "date": "2020-12-06T23:00:58Z",
            "amount": 29740,
            "currency_name": "Peso",
            "currency_code": "COP",
            "from": "Discover 3172601889670065",
            "to": "Discover 0720428384694643",
            "description": "Перевод с карты на карту",
        },
    ]


# ---------------------------------------------------------------------------
# Тесты: read_transactions_csv
# ---------------------------------------------------------------------------


class TestReadTransactionsCsv:
    """Тесты для функции read_transactions_csv."""

    @patch("src.readers.pd.read_csv")
    def test_returns_list_of_dicts(
        self, mock_csv: MagicMock, sample_df: pd.DataFrame, sample_records: List[Dict[str, Any]]
    ) -> None:
        """Валидный CSV возвращает список словарей."""
        mock_csv.return_value = sample_df
        result = read_transactions_csv("fake.csv")
        assert result == sample_records

    @patch("src.readers.pd.read_csv")
    def test_returns_correct_length(self, mock_csv: MagicMock, sample_df: pd.DataFrame) -> None:
        """Длина списка совпадает с числом строк в файле."""
        mock_csv.return_value = sample_df
        result = read_transactions_csv("fake.csv")
        assert len(result) == 2

    @patch("src.readers.pd.read_csv")
    def test_calls_read_csv_with_semicolon(self, mock_csv: MagicMock, sample_df: pd.DataFrame) -> None:
        """read_csv вызывается с разделителем ';'."""
        mock_csv.return_value = sample_df
        read_transactions_csv("data/transactions.csv")
        mock_csv.assert_called_once_with("data/transactions.csv", sep=";")

    @patch("src.readers.pd.read_csv", side_effect=FileNotFoundError("No such file"))
    def test_file_not_found(self, mock_csv: MagicMock) -> None:
        """Несуществующий файл → пустой список."""
        result = read_transactions_csv("nonexistent.csv")
        assert result == []

    @patch("src.readers.pd.read_csv", side_effect=pd.errors.EmptyDataError("No data"))
    def test_empty_file(self, mock_csv: MagicMock) -> None:
        """Пустой CSV → пустой список."""
        result = read_transactions_csv("empty.csv")
        assert result == []

    @patch("src.readers.pd.read_csv", side_effect=pd.errors.ParserError("Parse error"))
    def test_parser_error(self, mock_csv: MagicMock) -> None:
        """Некорректный CSV → пустой список."""
        result = read_transactions_csv("bad.csv")
        assert result == []

    @patch("src.readers.pd.read_csv", side_effect=OSError("Permission denied"))
    def test_os_error(self, mock_csv: MagicMock) -> None:
        """OSError при чтении → пустой список."""
        result = read_transactions_csv("no_access.csv")
        assert result == []

    @patch("src.readers.pd.read_csv")
    def test_empty_dataframe(self, mock_csv: MagicMock) -> None:
        """Файл с заголовками, но без данных → пустой список."""
        mock_csv.return_value = pd.DataFrame(columns=["id", "state", "date"])
        result = read_transactions_csv("headers_only.csv")
        assert result == []

    @patch("src.readers.pd.read_csv")
    def test_preserves_all_columns(self, mock_csv: MagicMock, sample_df: pd.DataFrame) -> None:
        """Все столбцы сохраняются в словаре."""
        mock_csv.return_value = sample_df
        result = read_transactions_csv("fake.csv")
        expected_keys = {"id", "state", "date", "amount", "currency_name", "currency_code", "from", "to", "description"}
        assert set(result[0].keys()) == expected_keys

    def test_real_csv_file(self) -> None:
        """Интеграционный тест: реальный CSV-файл читается корректно."""
        result = read_transactions_csv("data/transactions.csv")
        assert len(result) == 1000
        assert result[0]["state"] in ("EXECUTED", "CANCELED", "PENDING")


# ---------------------------------------------------------------------------
# Тесты: read_transactions_xlsx
# ---------------------------------------------------------------------------


class TestReadTransactionsXlsx:
    """Тесты для функции read_transactions_xlsx."""

    @patch("src.readers.pd.read_excel")
    def test_returns_list_of_dicts(
        self, mock_xl: MagicMock, sample_df: pd.DataFrame, sample_records: List[Dict[str, Any]]
    ) -> None:
        """Валидный Excel возвращает список словарей."""
        mock_xl.return_value = sample_df
        result = read_transactions_xlsx("fake.xlsx")
        assert result == sample_records

    @patch("src.readers.pd.read_excel")
    def test_returns_correct_length(self, mock_xl: MagicMock, sample_df: pd.DataFrame) -> None:
        """Длина списка совпадает с числом строк."""
        mock_xl.return_value = sample_df
        result = read_transactions_xlsx("fake.xlsx")
        assert len(result) == 2

    @patch("src.readers.pd.read_excel")
    def test_calls_read_excel(self, mock_xl: MagicMock, sample_df: pd.DataFrame) -> None:
        """read_excel вызывается с правильным путём."""
        mock_xl.return_value = sample_df
        read_transactions_xlsx("data/transactions_excel.xlsx")
        mock_xl.assert_called_once_with("data/transactions_excel.xlsx")

    @patch("src.readers.pd.read_excel", side_effect=FileNotFoundError("No such file"))
    def test_file_not_found(self, mock_xl: MagicMock) -> None:
        """Несуществующий файл → пустой список."""
        result = read_transactions_xlsx("nonexistent.xlsx")
        assert result == []

    @patch("src.readers.pd.read_excel", side_effect=ValueError("Invalid file"))
    def test_invalid_file(self, mock_xl: MagicMock) -> None:
        """Невалидный Excel → пустой список."""
        result = read_transactions_xlsx("bad.xlsx")
        assert result == []

    @patch("src.readers.pd.read_excel", side_effect=OSError("Permission denied"))
    def test_os_error(self, mock_xl: MagicMock) -> None:
        """OSError при чтении → пустой список."""
        result = read_transactions_xlsx("no_access.xlsx")
        assert result == []

    @patch("src.readers.pd.read_excel")
    def test_empty_dataframe(self, mock_xl: MagicMock) -> None:
        """Файл с заголовками, но без данных → пустой список."""
        mock_xl.return_value = pd.DataFrame(columns=["id", "state", "date"])
        result = read_transactions_xlsx("headers_only.xlsx")
        assert result == []

    @patch("src.readers.pd.read_excel")
    def test_preserves_all_columns(self, mock_xl: MagicMock, sample_df: pd.DataFrame) -> None:
        """Все столбцы сохраняются в словаре."""
        mock_xl.return_value = sample_df
        result = read_transactions_xlsx("fake.xlsx")
        expected_keys = {"id", "state", "date", "amount", "currency_name", "currency_code", "from", "to", "description"}
        assert set(result[0].keys()) == expected_keys

    def test_real_xlsx_file(self) -> None:
        """Интеграционный тест: реальный Excel-файл читается корректно."""
        result = read_transactions_xlsx("data/transactions_excel.xlsx")
        assert len(result) == 1000
        assert result[0]["state"] in ("EXECUTED", "CANCELED", "PENDING")

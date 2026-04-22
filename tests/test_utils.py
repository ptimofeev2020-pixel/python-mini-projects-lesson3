"""Тесты для модуля src.utils — чтение JSON-файлов с транзакциями."""

import json
from typing import Any
from typing import Dict
from typing import List
from unittest.mock import mock_open
from unittest.mock import patch

import pytest

from src.utils import read_transactions_json

# ---------------------------------------------------------------------------
# Фикстуры
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_transactions() -> List[Dict[str, Any]]:
    """Пример корректного списка транзакций."""
    return [
        {
            "id": 441945886,
            "state": "EXECUTED",
            "date": "2019-08-26T10:50:58.294041",
            "operationAmount": {
                "amount": "31957.58",
                "currency": {"name": "руб.", "code": "RUB"},
            },
            "description": "Перевод организации",
            "from": "Maestro 1596837868705199",
            "to": "Счет 64686473678894779589",
        },
        {
            "id": 41428829,
            "state": "EXECUTED",
            "date": "2019-07-03T18:35:29.512364",
            "operationAmount": {
                "amount": "8221.37",
                "currency": {"name": "USD", "code": "USD"},
            },
            "description": "Перевод организации",
            "from": "MasterCard 7158300734726758",
            "to": "Счет 35383033474447895560",
        },
    ]


# ---------------------------------------------------------------------------
# Тесты: корректные данные
# ---------------------------------------------------------------------------


class TestReadTransactionsJsonValid:
    """Тесты для корректных JSON-файлов."""

    def test_reads_valid_json_list(self, sample_transactions: List[Dict[str, Any]], tmp_path: Any) -> None:
        """Файл с валидным списком транзакций возвращается как есть."""
        file = tmp_path / "ops.json"
        file.write_text(json.dumps(sample_transactions), encoding="utf-8")
        result = read_transactions_json(str(file))
        assert result == sample_transactions

    def test_returns_correct_length(self, sample_transactions: List[Dict[str, Any]], tmp_path: Any) -> None:
        """Длина возвращённого списка совпадает с количеством транзакций в файле."""
        file = tmp_path / "ops.json"
        file.write_text(json.dumps(sample_transactions), encoding="utf-8")
        result = read_transactions_json(str(file))
        assert len(result) == 2

    def test_empty_list_in_file(self, tmp_path: Any) -> None:
        """Файл с пустым JSON-списком возвращает пустой список."""
        file = tmp_path / "empty_list.json"
        file.write_text("[]", encoding="utf-8")
        result = read_transactions_json(str(file))
        assert result == []

    def test_single_transaction(self, tmp_path: Any) -> None:
        """Файл с одной транзакцией возвращает список из одного элемента."""
        txn = [{"id": 1, "state": "EXECUTED"}]
        file = tmp_path / "single.json"
        file.write_text(json.dumps(txn), encoding="utf-8")
        result = read_transactions_json(str(file))
        assert result == txn
        assert len(result) == 1

    def test_preserves_nested_structure(self, sample_transactions: List[Dict[str, Any]], tmp_path: Any) -> None:
        """Вложенные структуры (operationAmount, currency) сохраняются."""
        file = tmp_path / "ops.json"
        file.write_text(json.dumps(sample_transactions), encoding="utf-8")
        result = read_transactions_json(str(file))
        assert result[0]["operationAmount"]["currency"]["code"] == "RUB"
        assert result[1]["operationAmount"]["amount"] == "8221.37"


# ---------------------------------------------------------------------------
# Тесты: ошибки чтения / невалидные данные
# ---------------------------------------------------------------------------


class TestReadTransactionsJsonInvalid:
    """Тесты для некорректных или отсутствующих файлов."""

    def test_file_not_found(self) -> None:
        """Несуществующий файл → пустой список."""
        result = read_transactions_json("/nonexistent/path/ops.json")
        assert result == []

    def test_empty_file(self, tmp_path: Any) -> None:
        """Пустой файл (невалидный JSON) → пустой список."""
        file = tmp_path / "empty.json"
        file.write_text("", encoding="utf-8")
        result = read_transactions_json(str(file))
        assert result == []

    def test_invalid_json(self, tmp_path: Any) -> None:
        """Файл с некорректным JSON → пустой список."""
        file = tmp_path / "bad.json"
        file.write_text("{not valid json!!!", encoding="utf-8")
        result = read_transactions_json(str(file))
        assert result == []

    def test_json_dict_instead_of_list(self, tmp_path: Any) -> None:
        """Файл с JSON-объектом (не списком) → пустой список."""
        file = tmp_path / "dict.json"
        file.write_text('{"key": "value"}', encoding="utf-8")
        result = read_transactions_json(str(file))
        assert result == []

    def test_json_string_instead_of_list(self, tmp_path: Any) -> None:
        """Файл с JSON-строкой → пустой список."""
        file = tmp_path / "string.json"
        file.write_text('"just a string"', encoding="utf-8")
        result = read_transactions_json(str(file))
        assert result == []

    def test_json_number_instead_of_list(self, tmp_path: Any) -> None:
        """Файл с JSON-числом → пустой список."""
        file = tmp_path / "number.json"
        file.write_text("42", encoding="utf-8")
        result = read_transactions_json(str(file))
        assert result == []

    def test_json_null_instead_of_list(self, tmp_path: Any) -> None:
        """Файл с JSON null → пустой список."""
        file = tmp_path / "null.json"
        file.write_text("null", encoding="utf-8")
        result = read_transactions_json(str(file))
        assert result == []

    @patch("builtins.open", side_effect=OSError("Permission denied"))
    def test_os_error(self, mock_file: Any) -> None:
        """OSError при чтении файла → пустой список."""
        result = read_transactions_json("/some/path.json")
        assert result == []


# ---------------------------------------------------------------------------
# Тесты с mock_open
# ---------------------------------------------------------------------------


class TestReadTransactionsJsonMock:
    """Тесты с использованием mock_open для подмены файлового ввода."""

    @patch("builtins.open", mock_open(read_data='[{"id": 1}]'))
    def test_mock_open_valid_list(self) -> None:
        """mock_open: валидный JSON-список читается корректно."""
        result = read_transactions_json("fake_path.json")
        assert result == [{"id": 1}]

    @patch("builtins.open", mock_open(read_data="{}"))
    def test_mock_open_dict(self) -> None:
        """mock_open: JSON-объект возвращает пустой список."""
        result = read_transactions_json("fake_path.json")
        assert result == []

    @patch("builtins.open", mock_open(read_data=""))
    def test_mock_open_empty(self) -> None:
        """mock_open: пустая строка возвращает пустой список."""
        result = read_transactions_json("fake_path.json")
        assert result == []

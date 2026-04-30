"""Тесты модуля src.processing."""

from typing import Any
from typing import Dict
from typing import List

import pytest

from src.processing import filter_by_state
from src.processing import process_bank_operations
from src.processing import process_bank_search
from src.processing import sort_by_date


class TestFilterByState:
    """Тесты функции filter_by_state."""

    def test_default_state_executed(self, sample_operations: List[Dict[str, Any]]) -> None:
        """По умолчанию возвращаются операции со статусом EXECUTED."""
        result = filter_by_state(sample_operations)
        assert len(result) == 2
        assert all(op["state"] == "EXECUTED" for op in result)

    @pytest.mark.parametrize(
        ("state", "expected_count"),
        [
            ("EXECUTED", 2),
            ("CANCELED", 2),
            ("PENDING", 1),
        ],
    )
    def test_filter_by_various_states(
        self,
        sample_operations: List[Dict[str, Any]],
        state: str,
        expected_count: int,
    ) -> None:
        """Фильтрация по разным статусам."""
        result = filter_by_state(sample_operations, state)
        assert len(result) == expected_count
        assert all(op["state"] == state for op in result)

    def test_filter_no_matches(self, sample_operations: List[Dict[str, Any]]) -> None:
        """Отсутствие операций с указанным статусом → пустой список."""
        assert filter_by_state(sample_operations, "UNKNOWN") == []

    def test_filter_empty_list(self, empty_operations: List[Dict[str, Any]]) -> None:
        """Фильтрация пустого списка возвращает пустой список."""
        assert filter_by_state(empty_operations) == []
        assert filter_by_state(empty_operations, "EXECUTED") == []

    def test_filter_returns_list(self, sample_operations: List[Dict[str, Any]]) -> None:
        """Результат — список."""
        assert isinstance(filter_by_state(sample_operations), list)

    def test_filter_does_not_mutate_input(self, sample_operations: List[Dict[str, Any]]) -> None:
        """Исходный список не изменяется."""
        original_len = len(sample_operations)
        filter_by_state(sample_operations)
        assert len(sample_operations) == original_len


class TestSortByDate:
    """Тесты функции sort_by_date."""

    def test_sort_descending_default(self, sample_operations: List[Dict[str, Any]]) -> None:
        """По умолчанию сортировка по убыванию (новые сначала)."""
        result = sort_by_date(sample_operations)
        dates = [op["date"] for op in result]
        assert dates == sorted(dates, reverse=True)

    def test_sort_ascending(self, sample_operations: List[Dict[str, Any]]) -> None:
        """descending=False → сортировка по возрастанию."""
        result = sort_by_date(sample_operations, descending=False)
        dates = [op["date"] for op in result]
        assert dates == sorted(dates)

    @pytest.mark.parametrize(
        ("descending", "expected_first_id"),
        [
            (True, 999999999),  # 2020-01-01
            (False, 939719570),  # 2018-06-30
        ],
    )
    def test_sort_order_matches_expectation(
        self,
        sample_operations: List[Dict[str, Any]],
        descending: bool,
        expected_first_id: int,
    ) -> None:
        """Первый элемент совпадает с ожиданием для разных порядков сортировки."""
        result = sort_by_date(sample_operations, descending=descending)
        assert result[0]["id"] == expected_first_id

    def test_sort_same_dates_preserves_length(
        self, operations_same_date: List[Dict[str, Any]]
    ) -> None:
        """Операции с одинаковой датой корректно обрабатываются."""
        result = sort_by_date(operations_same_date)
        assert len(result) == 3

    def test_sort_empty_list(self, empty_operations: List[Dict[str, Any]]) -> None:
        """Сортировка пустого списка возвращает пустой список."""
        assert sort_by_date(empty_operations) == []

    def test_sort_returns_new_list(self, sample_operations: List[Dict[str, Any]]) -> None:
        """Возвращается новый список, исходный не изменяется."""
        original = list(sample_operations)
        sort_by_date(sample_operations)
        assert sample_operations == original

    def test_sort_invalid_date_raises(self) -> None:
        """Некорректный формат даты → ValueError."""
        bad = [{"id": 1, "state": "EXECUTED", "date": "not-a-date"}]
        with pytest.raises(ValueError):
            sort_by_date(bad)

    def test_sort_missing_date_raises(self) -> None:
        """Отсутствие ключа date → KeyError."""
        bad = [{"id": 1, "state": "EXECUTED"}]
        with pytest.raises(KeyError):
            sort_by_date(bad)

    def test_sort_single_element(self) -> None:
        """Список из одного элемента возвращается как есть."""
        single = [{"id": 1, "state": "EXECUTED", "date": "2020-01-01T00:00:00.000000"}]
        assert sort_by_date(single) == single


# ---------------------------------------------------------------------------
# Тесты: process_bank_search
# ---------------------------------------------------------------------------


class TestProcessBankSearch:
    """Тесты функции process_bank_search."""

    @pytest.fixture
    def search_data(self) -> List[Dict[str, Any]]:
        return [
            {"id": 1, "description": "Перевод организации"},
            {"id": 2, "description": "Перевод с карты на карту"},
            {"id": 3, "description": "Открытие вклада"},
            {"id": 4, "description": "Перевод со счета на счет"},
        ]

    def test_search_exact_match(self, search_data: List[Dict[str, Any]]) -> None:
        """Точное совпадение по описанию."""
        result = process_bank_search(search_data, "Открытие вклада")
        assert len(result) == 1
        assert result[0]["id"] == 3

    def test_search_partial_match(self, search_data: List[Dict[str, Any]]) -> None:
        """Частичное совпадение — ищет подстроку."""
        result = process_bank_search(search_data, "Перевод")
        assert len(result) == 3

    def test_search_case_insensitive(self, search_data: List[Dict[str, Any]]) -> None:
        """Поиск регистронезависимый."""
        result = process_bank_search(search_data, "перевод")
        assert len(result) == 3

    def test_search_no_match(self, search_data: List[Dict[str, Any]]) -> None:
        """Нет совпадений → пустой список."""
        result = process_bank_search(search_data, "Пополнение")
        assert result == []

    def test_search_empty_list(self) -> None:
        """Поиск в пустом списке → пустой список."""
        assert process_bank_search([], "test") == []

    def test_search_regex_pattern(self, search_data: List[Dict[str, Any]]) -> None:
        """Поддержка регулярных выражений."""
        result = process_bank_search(search_data, r"карт[уы]")
        assert len(result) == 1
        assert result[0]["id"] == 2

    def test_search_missing_description(self) -> None:
        """Транзакция без поля description не вызывает ошибку."""
        data: List[Dict[str, Any]] = [{"id": 1}, {"id": 2, "description": "Перевод"}]
        result = process_bank_search(data, "Перевод")
        assert len(result) == 1


# ---------------------------------------------------------------------------
# Тесты: process_bank_operations
# ---------------------------------------------------------------------------


class TestProcessBankOperations:
    """Тесты функции process_bank_operations."""

    @pytest.fixture
    def ops_data(self) -> List[Dict[str, Any]]:
        return [
            {"description": "Перевод организации"},
            {"description": "Перевод организации"},
            {"description": "Перевод организации"},
            {"description": "Открытие вклада"},
            {"description": "Перевод с карты на карту"},
            {"description": "Перевод с карты на карту"},
        ]

    def test_count_categories(self, ops_data: List[Dict[str, Any]]) -> None:
        """Подсчёт по заданным категориям."""
        categories = ["Перевод организации", "Открытие вклада", "Перевод с карты на карту"]
        result = process_bank_operations(ops_data, categories)
        assert result == {
            "Перевод организации": 3,
            "Открытие вклада": 1,
            "Перевод с карты на карту": 2,
        }

    def test_missing_category_returns_zero(self, ops_data: List[Dict[str, Any]]) -> None:
        """Категория, которой нет в данных, получает 0."""
        result = process_bank_operations(ops_data, ["Несуществующая"])
        assert result == {"Несуществующая": 0}

    def test_empty_data(self) -> None:
        """Пустой список данных → все категории по 0."""
        result = process_bank_operations([], ["Перевод организации"])
        assert result == {"Перевод организации": 0}

    def test_empty_categories(self, ops_data: List[Dict[str, Any]]) -> None:
        """Пустой список категорий → пустой словарь."""
        result = process_bank_operations(ops_data, [])
        assert result == {}

    def test_returns_dict(self, ops_data: List[Dict[str, Any]]) -> None:
        """Результат — словарь."""
        result = process_bank_operations(ops_data, ["Открытие вклада"])
        assert isinstance(result, dict)

    def test_partial_categories(self, ops_data: List[Dict[str, Any]]) -> None:
        """Подсчёт только указанных категорий, остальные игнорируются."""
        result = process_bank_operations(ops_data, ["Открытие вклада"])
        assert result == {"Открытие вклада": 1}
        assert "Перевод организации" not in result

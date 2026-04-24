"""Тесты модуля src.generators."""

from typing import Any
from typing import Dict
from typing import List

import pytest

from src.generators import card_number_generator
from src.generators import filter_by_currency
from src.generators import transaction_descriptions


@pytest.fixture
def transactions() -> List[Dict[str, Any]]:
    """Набор транзакций с разными валютами."""
    return [
        {
            "id": 939719570,
            "state": "EXECUTED",
            "date": "2018-06-30T02:08:58.425572",
            "operationAmount": {"amount": "9824.07", "currency": {"name": "USD", "code": "USD"}},
            "description": "Перевод организации",
            "from": "Счет 75106830613657916952",
            "to": "Счет 11776614605963066702",
        },
        {
            "id": 142264268,
            "state": "EXECUTED",
            "date": "2019-04-04T23:20:05.206878",
            "operationAmount": {"amount": "79114.93", "currency": {"name": "USD", "code": "USD"}},
            "description": "Перевод со счета на счет",
            "from": "Счет 19708645243227258542",
            "to": "Счет 75651667383060284188",
        },
        {
            "id": 873106923,
            "state": "EXECUTED",
            "date": "2019-03-23T01:09:46.296404",
            "operationAmount": {"amount": "43318.34", "currency": {"name": "руб.", "code": "RUB"}},
            "description": "Перевод со счета на счет",
            "from": "Счет 44812258784861134719",
            "to": "Счет 74489636417521191160",
        },
        {
            "id": 895315941,
            "state": "EXECUTED",
            "date": "2018-08-19T04:27:37.904916",
            "operationAmount": {"amount": "56883.54", "currency": {"name": "USD", "code": "USD"}},
            "description": "Перевод с карты на карту",
            "from": "Visa Classic 6831982476737658",
            "to": "Visa Platinum 8990922113665229",
        },
        {
            "id": 594226727,
            "state": "CANCELED",
            "date": "2018-09-12T21:27:25.241689",
            "operationAmount": {"amount": "67314.70", "currency": {"name": "руб.", "code": "RUB"}},
            "description": "Перевод организации",
            "from": "Visa Platinum 1246377376343588",
            "to": "Счет 14211924144426031657",
        },
    ]


class TestFilterByCurrency:
    """Тесты функции filter_by_currency."""

    def test_filter_usd(self, transactions: List[Dict[str, Any]]) -> None:
        """Фильтрация по USD возвращает только долларовые транзакции."""
        usd = filter_by_currency(transactions, "USD")
        result = list(usd)
        assert len(result) == 3
        assert all(
            t["operationAmount"]["currency"]["code"] == "USD" for t in result
        )

    def test_filter_rub(self, transactions: List[Dict[str, Any]]) -> None:
        """Фильтрация по RUB возвращает только рублёвые транзакции."""
        rub = filter_by_currency(transactions, "RUB")
        result = list(rub)
        assert len(result) == 2
        assert all(
            t["operationAmount"]["currency"]["code"] == "RUB" for t in result
        )

    def test_filter_no_matches(self, transactions: List[Dict[str, Any]]) -> None:
        """Нет транзакций с данной валютой → пустой итератор."""
        eur = filter_by_currency(transactions, "EUR")
        assert list(eur) == []

    def test_filter_empty_list(self) -> None:
        """Пустой список → пустой итератор."""
        assert list(filter_by_currency([], "USD")) == []

    def test_filter_returns_iterator(self, transactions: List[Dict[str, Any]]) -> None:
        """Результат — итератор, поддерживает next()."""
        usd = filter_by_currency(transactions, "USD")
        first = next(usd)
        assert first["id"] == 939719570

    def test_filter_preserves_order(self, transactions: List[Dict[str, Any]]) -> None:
        """Порядок транзакций сохраняется."""
        usd = list(filter_by_currency(transactions, "USD"))
        assert [t["id"] for t in usd] == [939719570, 142264268, 895315941]

    @pytest.mark.parametrize(
        ("currency", "expected_count"),
        [
            ("USD", 3),
            ("RUB", 2),
            ("EUR", 0),
        ],
    )
    def test_filter_parametrized(
        self,
        transactions: List[Dict[str, Any]],
        currency: str,
        expected_count: int,
    ) -> None:
        """Параметризованная проверка количества по разным валютам."""
        assert len(list(filter_by_currency(transactions, currency))) == expected_count

    def test_filter_missing_operation_amount(self) -> None:
        """Транзакция без operationAmount пропускается без ошибки."""
        txns = [{"id": 1, "description": "test"}]
        assert list(filter_by_currency(txns, "USD")) == []


class TestTransactionDescriptions:
    """Тесты генератора transaction_descriptions."""

    def test_all_descriptions(self, transactions: List[Dict[str, Any]]) -> None:
        """Возвращает описания всех транзакций по порядку."""
        gen = transaction_descriptions(transactions)
        result = list(gen)
        assert result == [
            "Перевод организации",
            "Перевод со счета на счет",
            "Перевод со счета на счет",
            "Перевод с карты на карту",
            "Перевод организации",
        ]

    def test_descriptions_count(self, transactions: List[Dict[str, Any]]) -> None:
        """Количество описаний равно количеству транзакций."""
        assert len(list(transaction_descriptions(transactions))) == 5

    def test_empty_list(self) -> None:
        """Пустой список → пустой генератор."""
        assert list(transaction_descriptions([])) == []

    def test_single_transaction(self) -> None:
        """Одна транзакция — одно описание."""
        txns = [{"description": "Тест"}]
        assert list(transaction_descriptions(txns)) == ["Тест"]

    def test_is_generator(self, transactions: List[Dict[str, Any]]) -> None:
        """Результат — генератор, поддерживает next()."""
        gen = transaction_descriptions(transactions)
        assert next(gen) == "Перевод организации"
        assert next(gen) == "Перевод со счета на счет"

    def test_various_count(self) -> None:
        """Различное количество транзакций."""
        for n in (1, 3, 10):
            txns = [{"description": f"desc_{i}"} for i in range(n)]
            assert len(list(transaction_descriptions(txns))) == n


class TestCardNumberGenerator:
    """Тесты генератора card_number_generator."""

    def test_basic_range(self) -> None:
        """Генерация 1–5 совпадает с ожиданием из ТЗ."""
        result = list(card_number_generator(1, 5))
        assert result == [
            "0000 0000 0000 0001",
            "0000 0000 0000 0002",
            "0000 0000 0000 0003",
            "0000 0000 0000 0004",
            "0000 0000 0000 0005",
        ]

    def test_format_16_digits_4_groups(self) -> None:
        """Формат: 4 группы по 4 цифры через пробел."""
        card = next(card_number_generator(1, 1))
        parts = card.split(" ")
        assert len(parts) == 4
        assert all(len(p) == 4 for p in parts)

    def test_single_value(self) -> None:
        """Один элемент диапазона."""
        result = list(card_number_generator(100, 100))
        assert result == ["0000 0000 0000 0100"]

    @pytest.mark.parametrize(
        ("start", "end", "expected_first", "expected_last"),
        [
            (1, 1, "0000 0000 0000 0001", "0000 0000 0000 0001"),
            (9999999999999998, 9999999999999999, "9999 9999 9999 9998", "9999 9999 9999 9999"),
            (10, 12, "0000 0000 0000 0010", "0000 0000 0000 0012"),
        ],
        ids=["min_range", "max_range", "mid_range"],
    )
    def test_boundary_values(
        self, start: int, end: int, expected_first: str, expected_last: str
    ) -> None:
        """Крайние значения диапазона."""
        result = list(card_number_generator(start, end))
        assert result[0] == expected_first
        assert result[-1] == expected_last

    def test_count(self) -> None:
        """Количество сгенерированных номеров = end - start + 1."""
        result = list(card_number_generator(1, 100))
        assert len(result) == 100

    def test_leading_zeros(self) -> None:
        """Маленькие числа дополняются ведущими нулями до 16 цифр."""
        card = next(card_number_generator(1, 1))
        assert card.replace(" ", "").isdigit()
        assert len(card.replace(" ", "")) == 16

    def test_is_generator(self) -> None:
        """Результат — генератор, поддерживает next()."""
        gen = card_number_generator(1, 3)
        assert next(gen) == "0000 0000 0000 0001"
        assert next(gen) == "0000 0000 0000 0002"

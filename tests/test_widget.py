"""Тесты модуля src.widget."""

import pytest

from src.widget import get_date
from src.widget import mask_account_card


class TestMaskAccountCard:
    """Тесты функции mask_account_card."""

    @pytest.mark.parametrize(
        ("entry", "expected"),
        [
            ("Maestro 1596837868705199", "Maestro 1596 83** **** 5199"),
            ("MasterCard 7158300734726758", "MasterCard 7158 30** **** 6758"),
            ("Visa Classic 6831982476737658", "Visa Classic 6831 98** **** 7658"),
            ("Visa Platinum 8990922113665229", "Visa Platinum 8990 92** **** 5229"),
            ("Visa Gold 5999414228426353", "Visa Gold 5999 41** **** 6353"),
        ],
        ids=[
            "maestro",
            "mastercard",
            "visa_classic",
            "visa_platinum",
            "visa_gold",
        ],
    )
    def test_mask_cards(self, entry: str, expected: str) -> None:
        """Разные типы карт маскируются корректно."""
        assert mask_account_card(entry) == expected

    @pytest.mark.parametrize(
        ("entry", "expected"),
        [
            ("Счет 64686473678894779589", "Счет **9589"),
            ("Счет 35383033474447895560", "Счет **5560"),
            ("Счет 73654108430135874305", "Счет **4305"),
            ("Счет 12345678", "Счет **5678"),
        ],
    )
    def test_mask_accounts(self, entry: str, expected: str) -> None:
        """Счета маскируются корректно."""
        assert mask_account_card(entry) == expected

    @pytest.mark.parametrize(
        "invalid",
        ["", "Visa", "1596837868705199"],
    )
    def test_invalid_format_raises(self, invalid: str) -> None:
        """Строка без пробела → ValueError."""
        with pytest.raises(ValueError):
            mask_account_card(invalid)

    def test_invalid_card_number_propagates(self) -> None:
        """Некорректный номер карты в составе строки → ValueError."""
        with pytest.raises(ValueError):
            mask_account_card("Visa 1234")

    def test_invalid_account_propagates(self) -> None:
        """Слишком короткий номер счёта → ValueError."""
        with pytest.raises(ValueError):
            mask_account_card("Счет 12")


class TestGetDate:
    """Тесты функции get_date."""

    @pytest.mark.parametrize(
        ("date_str", "expected"),
        [
            ("2024-03-11T02:26:18.671407", "11.03.2024"),
            ("2025-12-01T15:00:00.000000", "01.12.2025"),
            ("2000-01-09T00:00:00.000000", "09.01.2000"),
            ("1999-12-31T23:59:59.999999", "31.12.1999"),
            ("2024-02-29T12:00:00.000000", "29.02.2024"),  # високосный год
        ],
        ids=["standard", "year_2025", "year_2000", "end_of_millennium", "leap_year"],
    )
    def test_get_date_valid(self, date_str: str, expected: str) -> None:
        """Корректное преобразование ISO → ДД.ММ.ГГГГ."""
        assert get_date(date_str) == expected

    @pytest.mark.parametrize(
        "invalid",
        [
            "",
            "not-a-date",
            "2024/03/11",
            "11.03.2024",
            "2024-13-01T00:00:00.000000",  # несуществующий месяц
        ],
    )
    def test_get_date_invalid_raises(self, invalid: str) -> None:
        """Некорректная строка → ValueError."""
        with pytest.raises(ValueError):
            get_date(invalid)

    def test_get_date_returns_string(self) -> None:
        """Результат — строка."""
        result = get_date("2024-03-11T02:26:18.671407")
        assert isinstance(result, str)
        assert len(result) == 10

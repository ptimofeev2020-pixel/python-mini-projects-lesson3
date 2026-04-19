"""Тесты модуля src.masks."""

import pytest

from src.masks import get_mask_account
from src.masks import get_mask_card_number


class TestGetMaskCardNumber:
    """Тесты функции get_mask_card_number."""

    @pytest.mark.parametrize(
        ("card_number", "expected"),
        [
            ("7000792289606361", "7000 79** **** 6361"),
            ("1596837868705199", "1596 83** **** 5199"),
            ("1234567890123456", "1234 56** **** 3456"),
            ("0000000000000000", "0000 00** **** 0000"),
            ("9999999999999999", "9999 99** **** 9999"),
        ],
        ids=[
            "card_as_string_1",
            "card_as_string_2",
            "ascending_digits",
            "all_zeros",
            "all_nines",
        ],
    )
    def test_mask_card_number_from_string(self, card_number: str, expected: str) -> None:
        """Корректная маска для строкового номера карты."""
        assert get_mask_card_number(card_number) == expected

    @pytest.mark.parametrize(
        ("card_number", "expected"),
        [
            (7000792289606361, "7000 79** **** 6361"),
            (1596837868705199, "1596 83** **** 5199"),
            (6831982476737658, "6831 98** **** 7658"),
        ],
    )
    def test_mask_card_number_from_int(self, card_number: int, expected: str) -> None:
        """Корректная маска для числового номера карты."""
        assert get_mask_card_number(card_number) == expected

    def test_mask_card_number_with_spaces(self) -> None:
        """Пробелы в номере карты должны игнорироваться."""
        assert get_mask_card_number("7000 7922 8960 6361") == "7000 79** **** 6361"

    @pytest.mark.parametrize(
        "invalid",
        [
            "",
            "1234",
            "12345678901234567",  # 17 цифр
            "123456789012345",  # 15 цифр
            "abcdabcdabcdabcd",
            "7000-7922-8960-6361",
            "7000.7922.8960.6361",
        ],
    )
    def test_mask_card_number_invalid_raises(self, invalid: str) -> None:
        """Некорректный номер карты → ValueError."""
        with pytest.raises(ValueError):
            get_mask_card_number(invalid)

    def test_mask_card_number_returns_string(self) -> None:
        """Результат — строка."""
        assert isinstance(get_mask_card_number("7000792289606361"), str)


class TestGetMaskAccount:
    """Тесты функции get_mask_account."""

    @pytest.mark.parametrize(
        ("account_number", "expected"),
        [
            ("73654108430135874305", "**4305"),
            ("64686473678894779589", "**9589"),
            ("12345678", "**5678"),
            ("0000", "**0000"),
        ],
    )
    def test_mask_account_from_string(self, account_number: str, expected: str) -> None:
        """Корректная маска для строкового номера счёта."""
        assert get_mask_account(account_number) == expected

    @pytest.mark.parametrize(
        ("account_number", "expected"),
        [
            (73654108430135874305, "**4305"),
            (35383033474447895560, "**5560"),
            (1234, "**1234"),
        ],
    )
    def test_mask_account_from_int(self, account_number: int, expected: str) -> None:
        """Корректная маска для числового номера счёта."""
        assert get_mask_account(account_number) == expected

    @pytest.mark.parametrize("short", ["", "1", "12", "123"])
    def test_mask_account_too_short_raises(self, short: str) -> None:
        """Слишком короткий номер → ValueError."""
        with pytest.raises(ValueError):
            get_mask_account(short)

    def test_mask_account_exactly_four(self) -> None:
        """Граничный случай: ровно 4 символа."""
        assert get_mask_account("1234") == "**1234"

    def test_mask_account_returns_string(self) -> None:
        """Результат — строка."""
        assert isinstance(get_mask_account("12345678"), str)

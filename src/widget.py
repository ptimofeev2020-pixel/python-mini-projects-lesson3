"""Модуль widget — функции для отображения платёжных реквизитов."""

from datetime import datetime

from src.masks import get_mask_account
from src.masks import get_mask_card_number


def mask_account_card(account_or_card: str) -> str:
    """Маскирует номер карты или счёта в строке вида «<Название> <Номер>».

    Тип определяется по последнему слову перед номером:
    - если оно «Счет» — применяется маска счёта (**XXXX);
    - иначе — маска карты (XXXX XX** **** XXXX).

    Args:
        account_or_card: Строка вида «Visa Platinum 7000792289606361»
                         или «Счет 73654108430135874305».

    Returns:
        Строка с замаскированным номером, например:
        «Visa Platinum 7000 79** **** 6361» или «Счет **4305».

    Raises:
        ValueError: Если строка не содержит хотя бы двух слов.

    Example:
        >>> mask_account_card("Visa Platinum 7000792289606361")
        'Visa Platinum 7000 79** **** 6361'
        >>> mask_account_card("Счет 73654108430135874305")
        'Счет **4305'
    """
    parts = account_or_card.rsplit(maxsplit=1)
    if len(parts) < 2:
        raise ValueError(f"Ожидается строка вида '<Название> <Номер>', получено: '{account_or_card}'")

    name, number = parts

    if name == "Счет":
        masked = get_mask_account(number)
    else:
        masked = get_mask_card_number(number)

    return f"{name} {masked}"


def get_date(date_str: str) -> str:
    """Преобразует дату из формата ISO в формат ДД.ММ.ГГГГ.

    Args:
        date_str: Строка вида «2024-03-11T02:26:18.671407».

    Returns:
        Строка вида «11.03.2024».

    Example:
        >>> get_date("2024-03-11T02:26:18.671407")
        '11.03.2024'
    """
    return datetime.fromisoformat(date_str).strftime("%d.%m.%Y")

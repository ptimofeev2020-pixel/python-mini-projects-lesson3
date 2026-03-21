"""Модуль masks — функции для маскирования конфиденциальных данных."""


def get_mask_card_number(card_number: int | str) -> str:
    """Маскирует номер банковской карты.

    Принимает номер карты и возвращает маску в формате:
        XXXX XX** **** XXXX
    где X — цифры номера. Показаны первые 6 и последние 4 цифры,
    остальные скрыты звёздочками. Блоки разделяются пробелами.

    Args:
        card_number: Номер карты — строка или целое число (16 цифр).

    Returns:
        Маскированный номер карты в формате «XXXX XX** **** XXXX».

    Raises:
        ValueError: Если после удаления пробелов номер содержит не 16 цифр.

    Example:
        >>> get_mask_card_number("7000792289606361")
        '7000 79** **** 6361'
        >>> get_mask_card_number("7000 7922 8960 6361")
        '7000 79** **** 6361'
    """
    digits = str(card_number).replace(" ", "")

    if not digits.isdigit() or len(digits) != 16:
        raise ValueError(
            f"Номер карты должен содержать ровно 16 цифр, получено: '{card_number}'"
        )

    # XXXX XX** **** XXXX
    masked = f"{digits[:4]} {digits[4:6]}** **** {digits[12:]}"
    return masked


def get_mask_account(account_number: int | str) -> str:
    """Маскирует номер банковского счёта.

    Принимает номер счёта и возвращает маску в формате:
        **XXXX
    где показаны только последние 4 цифры, перед ними — две звёздочки.

    Args:
        account_number: Номер счёта — строка или целое число (минимум 4 цифры).

    Returns:
        Маскированный номер счёта в формате «**XXXX».

    Raises:
        ValueError: Если номер счёта содержит менее 4 символов.

    Example:
        >>> get_mask_account("73654108430135874305")
        '**4305'
    """
    account_number = str(account_number)
    if len(account_number) < 4:
        raise ValueError(
            f"Номер счёта должен содержать не менее 4 символов, получено: '{account_number}'"
        )

    return f"**{account_number[-4:]}"

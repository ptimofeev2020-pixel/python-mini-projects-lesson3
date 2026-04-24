"""Модуль masks — функции для маскирования конфиденциальных данных."""

import logging
import os

# ---------------------------------------------------------------------------
# Настройка логера модуля masks
# ---------------------------------------------------------------------------
logger = logging.getLogger("masks")
logger.setLevel(logging.DEBUG)

_log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(_log_dir, exist_ok=True)

_file_handler = logging.FileHandler(os.path.join(_log_dir, "masks.log"), mode="w", encoding="utf-8")
_file_handler.setLevel(logging.DEBUG)

_file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_file_handler.setFormatter(_file_formatter)

logger.addHandler(_file_handler)


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
    logger.info("Вызвана функция get_mask_card_number с аргументом: %s", type(card_number).__name__)
    digits = str(card_number).replace(" ", "")

    if not digits.isdigit() or len(digits) != 16:
        logger.error("Некорректный номер карты: '%s'", card_number)
        raise ValueError(f"Номер карты должен содержать ровно 16 цифр, получено: '{card_number}'")

    # XXXX XX** **** XXXX
    masked = f"{digits[:4]} {digits[4:6]}** **** {digits[12:]}"
    logger.info("Маска карты успешно сгенерирована: %s", masked)
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
    logger.info("Вызвана функция get_mask_account с аргументом: %s", type(account_number).__name__)
    account_number = str(account_number)
    if len(account_number) < 4:
        logger.error("Некорректный номер счёта: '%s'", account_number)
        raise ValueError(f"Номер счёта должен содержать не менее 4 символов, получено: '{account_number}'")

    masked = f"**{account_number[-4:]}"
    logger.info("Маска счёта успешно сгенерирована: %s", masked)
    return masked

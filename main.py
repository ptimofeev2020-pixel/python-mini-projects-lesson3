"""Точка входа проекта — демонстрация маскирования банковских реквизитов."""

from src.masks import get_mask_account
from src.masks import get_mask_card_number
from src.widget import mask_account_card


def main() -> None:
    """Запускает демонстрацию функций маскирования."""

    card_examples_str = [
        "7000792289606361",
        "1596837868705199",
    ]
    card_examples_int = [
        6831982476737658,
    ]

    account_examples_str = [
        "73654108430135874305",
    ]
    account_examples_int = [
        35383033474447895560,
    ]

    print("=" * 40)
    print("  Маскирование номеров карт (str)")
    print("=" * 40)
    for card in card_examples_str:
        print(f"  {card}  →  {get_mask_card_number(card)}")

    print()
    print("=" * 40)
    print("  Маскирование номеров карт (int)")
    print("=" * 40)
    for card in card_examples_int:
        print(f"  {card}  →  {get_mask_card_number(card)}")

    print()
    print("=" * 40)
    print("  Маскирование номеров счетов (str)")
    print("=" * 40)
    for account in account_examples_str:
        print(f"  {account}  →  {get_mask_account(account)}")

    print()
    print("=" * 40)
    print("  Маскирование номеров счетов (int)")
    print("=" * 40)
    for account in account_examples_int:
        print(f"  {account}  →  {get_mask_account(account)}")

    print()
    print("=" * 40)
    print("  mask_account_card")
    print("=" * 40)
    widget_examples = [
        "Maestro 1596837868705199",
        "Счет 64686473678894779589",
        "MasterCard 7158300734726758",
        "Счет 35383033474447895560",
        "Visa Classic 6831982476737658",
        "Visa Platinum 8990922113665229",
        "Visa Gold 5999414228426353",
        "Счет 73654108430135874305",
    ]
    for entry in widget_examples:
        print(f"  {entry}  →  {mask_account_card(entry)}")


if __name__ == "__main__":
    main()

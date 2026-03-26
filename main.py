"""Точка входа проекта — демонстрация маскирования банковских реквизитов."""

from src.masks import get_mask_account
from src.masks import get_mask_card_number
from src.widget import get_date
from src.widget import mask_account_card
from src.processing import filter_by_state, sort_by_date


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

    print()
    print("=" * 40)
    print("  get_date")
    print("=" * 40)
    date_examples = [
        "2024-03-11T02:26:18.671407",
        "2025-12-01T15:00:00.000000",
        "2000-01-09T00:00:00.000000",
    ]
    for date_str in date_examples:
        print(f"  {date_str}  →  {get_date(date_str)}")

    data = [
        {'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'},
        {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'},
        {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
        {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'}
    ]

    # Фильтрация по статусу EXECUTED
    executed = filter_by_state(data)  # по умолчанию 'EXECUTED'
    print(executed)
    # Ожидаем:
    # [
    #   {'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'},
    #   {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'}
    # ]

    # Фильтрация по статусу CANCELED
    canceled = filter_by_state(data, 'CANCELED')
    print(canceled)
    # Ожидаем:
    # [
    #   {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
    #   {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'}
    # ]

    # Сортировка по убыванию (descending=True)
    sorted_desc = sort_by_date(data)  # по умолчанию True
    print(sorted_desc)
    # Ожидаем:
    # [
    #   {'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'},
    #   {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'},
    #   {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
    #   {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'}
    # ]

    # Сортировка по возрастанию (descending=False)
    sorted_asc = sort_by_date(data, descending=False)
    print(sorted_asc)
    # Ожидаем:
    # [
    #   {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'},
    #   {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
    #   {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'},
    #   {'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'}
    # ]

if __name__ == "__main__":
    main()

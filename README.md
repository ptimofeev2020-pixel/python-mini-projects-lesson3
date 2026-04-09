# MyProject

Утилита для маскирования конфиденциальных банковских реквизитов
и обработки банковских операций.

## Установка

```bash
# Клонирование репозитория
git clone <url>
cd MyProject

# Установка зависимостей
poetry install --with lint
```

## Возможности

### Модуль `masks`

#### `get_mask_card_number(card_number)`
Маскирует номер банковской карты по формату `XXXX XX** **** XXXX`.
Принимает строку или целое число (16 цифр).

```python
from src.masks import get_mask_card_number

get_mask_card_number("7000792289606361")  # → '7000 79** **** 6361'
get_mask_card_number(7000792289606361)    # → '7000 79** **** 6361'
```

#### `get_mask_account(account_number)`
Маскирует номер банковского счёта по формату `**XXXX`.
Принимает строку или целое число (минимум 4 цифры).

```python
from src.masks import get_mask_account

get_mask_account("73654108430135874305")  # → '**4305'
get_mask_account(73654108430135874305)    # → '**4305'
```

### Модуль `widget`

#### `mask_account_card(account_or_card)`
Маскирует номер карты или счёта в строке вида «Название Номер».

```python
from src.widget import mask_account_card

mask_account_card("Visa Platinum 7000792289606361")  # → 'Visa Platinum 7000 79** **** 6361'
mask_account_card("Счет 73654108430135874305")       # → 'Счет **4305'
```

#### `get_date(date_str)`
Преобразует дату из формата ISO в формат ДД.ММ.ГГГГ.

```python
from src.widget import get_date

get_date("2024-03-11T02:26:18.671407")  # → '11.03.2024'
```

### Модуль `processing`

#### `filter_by_state(operations, state='EXECUTED')`
Фильтрует список банковских операций по заданному статусу.
По умолчанию возвращает операции со статусом `EXECUTED`.

```python
from src.processing import filter_by_state

data = [
    {'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'},
    {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
]

filter_by_state(data)              # → только EXECUTED
filter_by_state(data, 'CANCELED')  # → только CANCELED
```

#### `sort_by_date(operations, descending=True)`
Сортирует список банковских операций по дате.
По умолчанию сортировка по убыванию (новые сначала).

```python
from src.processing import sort_by_date

sort_by_date(data)                    # по убыванию (новые → старые)
sort_by_date(data, descending=False)  # по возрастанию (старые → новые)
```

## Линтинг

```bash
# форматирование
poetry run black src tests main.py
poetry run isort src tests main.py

# проверка стиля
poetry run flake8 src tests main.py

# проверка типов
poetry run mypy src
```

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

### Модуль `generators`

#### `filter_by_currency(transactions, currency)`
Возвращает итератор, который поочерёдно выдаёт транзакции с указанным кодом валюты.

```python
from src.generators import filter_by_currency

transactions = [
    {"id": 1, "operationAmount": {"amount": "100", "currency": {"name": "USD", "code": "USD"}}, ...},
    {"id": 2, "operationAmount": {"amount": "200", "currency": {"name": "руб.", "code": "RUB"}}, ...},
]

usd_transactions = filter_by_currency(transactions, "USD")
print(next(usd_transactions))  # → транзакция с id=1
```

#### `transaction_descriptions(transactions)`
Генератор, который поочерёдно возвращает описание каждой транзакции.

```python
from src.generators import transaction_descriptions

descriptions = transaction_descriptions(transactions)
print(next(descriptions))  # → 'Перевод организации'
print(next(descriptions))  # → 'Перевод со счета на счет'
```

#### `card_number_generator(start, end)`
Генератор номеров банковских карт в формате `XXXX XXXX XXXX XXXX` в заданном диапазоне.

```python
from src.generators import card_number_generator

for card_number in card_number_generator(1, 5):
    print(card_number)
# 0000 0000 0000 0001
# 0000 0000 0000 0002
# ...
# 0000 0000 0000 0005
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

## Тестирование

Проект покрыт тестами на **pytest** с использованием фикстур и параметризации.
Покрытие кода — **100%** (порог не менее 80%).

### Установка зависимостей для тестов

```bash
poetry install --with test
```

### Запуск тестов

```bash
# Все тесты
poetry run pytest

# С подробным выводом
poetry run pytest -v

# Конкретный модуль
poetry run pytest tests/test_masks.py
poetry run pytest tests/test_widget.py
poetry run pytest tests/test_processing.py
poetry run pytest tests/test_generators.py
```

### Тесты с отчётом о покрытии

```bash
# Покрытие в терминал (с указанием непокрытых строк)
poetry run pytest --cov=src --cov-report=term-missing

# HTML-отчёт — генерируется в папку htmlcov/
poetry run pytest --cov=src --cov-report=html

# После — открыть htmlcov/index.html в браузере
```

### Структура тестов

```
tests/
├── __init__.py
├── conftest.py          # общие фикстуры (sample_operations и т.п.)
├── test_masks.py        # тесты src/masks.py
├── test_widget.py       # тесты src/widget.py
├── test_processing.py   # тесты src/processing.py
└── test_generators.py   # тесты src/generators.py
```

В тестах используются:
- `@pytest.fixture` — для подготовки входных данных (списки операций, пустые списки, данные с одинаковыми датами);
- `@pytest.mark.parametrize` — для покрытия разных кейсов без дублирования кода;
- негативные кейсы — проверка, что функции корректно падают с `ValueError` / `KeyError` на некорректных входных данных.

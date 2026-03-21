# MyProject

Утилита для маскирования конфиденциальных банковских реквизитов.

## Возможности

### `get_mask_card_number(card_number)`
Маскирует номер банковской карты по формату `XXXX XX** **** XXXX`.  
Принимает строку или целое число (16 цифр).

```python
from src.masks import get_mask_card_number

get_mask_card_number("7000792289606361")  # → '7000 79** **** 6361'
get_mask_card_number(7000792289606361)    # → '7000 79** **** 6361'
```

### `get_mask_account(account_number)`
Маскирует номер банковского счёта по формату `**XXXX`.  
Принимает строку или целое число (минимум 4 цифры).

```python
from src.masks import get_mask_account

get_mask_account("73654108430135874305")  # → '**4305'
get_mask_account(73654108430135874305)    # → '**4305'
```

## Установка зависимостей

```bash
poetry install --with lint
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

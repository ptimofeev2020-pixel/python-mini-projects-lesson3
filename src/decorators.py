"""Модуль decorators — декораторы для логирования выполнения функций."""

import functools
from typing import Any
from typing import Callable
from typing import Optional
from typing import TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def log(filename: Optional[str] = None) -> Callable[[F], F]:
    """Декоратор для автоматического логирования вызовов функций.

    Регистрирует имя функции, результат выполнения при успехе,
    а при ошибке — тип исключения и входные параметры.

    Args:
        filename: Путь к файлу для записи логов. Если ``None``,
                  логи выводятся в консоль (``print``).

    Returns:
        Декоратор, оборачивающий целевую функцию.

    Example:
        >>> @log(filename="mylog.txt")
        ... def my_function(x, y):
        ...     return x + y
        >>> my_function(1, 2)  # в mylog.txt: "my_function ok"
        3

        >>> @log()
        ... def my_function(x, y):
        ...     return x + y
        >>> my_function(1, 2)  # в консоль: "my_function ok"
        3
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                message = f"{func.__name__} error: {type(e).__name__}. Inputs: {args}, {kwargs}"
                _write_log(message, filename)
                raise
            else:
                message = f"{func.__name__} ok"
                _write_log(message, filename)
                return result

        return wrapper  # type: ignore[return-value]

    return decorator


def _write_log(message: str, filename: Optional[str] = None) -> None:
    """Записывает лог-сообщение в файл или в консоль.

    Args:
        message: Текст сообщения.
        filename: Путь к файлу. Если ``None`` — вывод в консоль.
    """
    if filename is not None:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(message + "\n")
    else:
        print(message)

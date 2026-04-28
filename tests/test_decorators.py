"""Тесты модуля src.decorators."""

import os
from typing import Any

import pytest

from src.decorators import log

# ── Вспомогательные декорированные функции ──────────────────────────────


def _make_add_console() -> Any:
    """Возвращает функцию сложения, логирующую в консоль."""

    @log()
    def add(x: int, y: int) -> int:
        return x + y

    return add


def _make_add_file(path: str) -> Any:
    """Возвращает функцию сложения, логирующую в файл."""

    @log(filename=path)
    def add(x: int, y: int) -> int:
        return x + y

    return add


def _make_fail_console() -> Any:
    """Возвращает функцию, бросающую ValueError, логирующую в консоль."""

    @log()
    def fail(x: int, y: int) -> None:
        raise ValueError("test error")

    return fail


def _make_fail_file(path: str) -> Any:
    """Возвращает функцию, бросающую ValueError, логирующую в файл."""

    @log(filename=path)
    def fail(x: int, y: int) -> None:
        raise ValueError("test error")

    return fail


# ── Тесты: вывод в консоль ──────────────────────────────────────────────


class TestLogConsole:
    """Тесты декоратора log при выводе в консоль (capsys)."""

    def test_success_message(self, capsys: pytest.CaptureFixture[str]) -> None:
        """При успешном выполнении выводится '<name> ok'."""
        add = _make_add_console()
        result = add(1, 2)
        assert result == 3
        captured = capsys.readouterr()
        assert captured.out.strip() == "add ok"

    def test_error_message(self, capsys: pytest.CaptureFixture[str]) -> None:
        """При ошибке выводится '<name> error: <type>. Inputs: <args>, <kwargs>'."""
        fail = _make_fail_console()
        with pytest.raises(ValueError):
            fail(1, 2)
        captured = capsys.readouterr()
        assert "fail error: ValueError. Inputs: (1, 2), {}" in captured.out

    def test_error_is_reraised(self) -> None:
        """Исключение пробрасывается наружу."""
        fail = _make_fail_console()
        with pytest.raises(ValueError, match="test error"):
            fail(1, 2)

    def test_return_value_preserved(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Возвращаемое значение функции сохраняется."""
        add = _make_add_console()
        assert add(10, 20) == 30

    @pytest.mark.parametrize(
        ("x", "y", "expected"),
        [(0, 0, 0), (-1, 1, 0), (100, 200, 300)],
    )
    def test_various_inputs(
        self, capsys: pytest.CaptureFixture[str], x: int, y: int, expected: int
    ) -> None:
        """Разные входные данные — результат корректен, лог 'ok'."""
        add = _make_add_console()
        assert add(x, y) == expected
        captured = capsys.readouterr()
        assert "add ok" in captured.out

    def test_kwargs_in_error(self, capsys: pytest.CaptureFixture[str]) -> None:
        """kwargs отображаются в сообщении об ошибке."""

        @log()
        def func(a: int, b: int = 0) -> int:
            raise TypeError("bad")

        with pytest.raises(TypeError):
            func(1, b=2)
        captured = capsys.readouterr()
        assert "func error: TypeError. Inputs: (1,), {'b': 2}" in captured.out

    def test_preserves_function_name(self) -> None:
        """Декоратор сохраняет __name__ оригинальной функции."""
        add = _make_add_console()
        assert add.__name__ == "add"


# ── Тесты: вывод в файл ─────────────────────────────────────────────────


class TestLogFile:
    """Тесты декоратора log при записи в файл."""

    def test_success_to_file(self, tmp_path: Any) -> None:
        """Успех → в файле '<name> ok'."""
        log_file = str(tmp_path / "test.log")
        add = _make_add_file(log_file)
        result = add(1, 2)
        assert result == 3
        content = open(log_file, encoding="utf-8").read()
        assert content.strip() == "add ok"

    def test_error_to_file(self, tmp_path: Any) -> None:
        """Ошибка → в файле '<name> error: ...'."""
        log_file = str(tmp_path / "test.log")
        fail = _make_fail_file(log_file)
        with pytest.raises(ValueError):
            fail(1, 2)
        content = open(log_file, encoding="utf-8").read()
        assert "fail error: ValueError. Inputs: (1, 2), {}" in content

    def test_file_created(self, tmp_path: Any) -> None:
        """Лог-файл создаётся автоматически."""
        log_file = str(tmp_path / "new.log")
        assert not os.path.exists(log_file)
        add = _make_add_file(log_file)
        add(1, 1)
        assert os.path.exists(log_file)

    def test_file_appends(self, tmp_path: Any) -> None:
        """Повторные вызовы дописывают лог, а не перезаписывают."""
        log_file = str(tmp_path / "test.log")
        add = _make_add_file(log_file)
        add(1, 2)
        add(3, 4)
        lines = open(log_file, encoding="utf-8").read().strip().split("\n")
        assert len(lines) == 2
        assert lines[0] == "add ok"
        assert lines[1] == "add ok"

    def test_no_console_output_when_file(
        self, tmp_path: Any, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """При записи в файл в консоль ничего не выводится."""
        log_file = str(tmp_path / "test.log")
        add = _make_add_file(log_file)
        add(1, 2)
        captured = capsys.readouterr()
        assert captured.out == ""

    @pytest.mark.parametrize(
        ("x", "y", "expected"),
        [(0, 0, 0), (5, 5, 10), (-3, 3, 0)],
    )
    def test_various_inputs_file(
        self, tmp_path: Any, x: int, y: int, expected: int
    ) -> None:
        """Разные входы — результат корректен, в файле 'ok'."""
        log_file = str(tmp_path / "test.log")
        add = _make_add_file(log_file)
        assert add(x, y) == expected


# ── Тесты: разные типы исключений ───────────────────────────────────────


class TestLogExceptionTypes:
    """Проверка логирования разных типов ошибок."""

    @pytest.mark.parametrize(
        ("exc_class", "exc_name"),
        [
            (ValueError, "ValueError"),
            (TypeError, "TypeError"),
            (ZeroDivisionError, "ZeroDivisionError"),
            (KeyError, "KeyError"),
        ],
    )
    def test_various_exceptions_console(
        self,
        capsys: pytest.CaptureFixture[str],
        exc_class: type,
        exc_name: str,
    ) -> None:
        """Тип ошибки корректно отображается в логе."""

        @log()
        def boom() -> None:
            raise exc_class("oops")

        with pytest.raises(exc_class):
            boom()
        captured = capsys.readouterr()
        assert f"boom error: {exc_name}" in captured.out

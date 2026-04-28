"""Тесты для модуля src.external_api — конвертация валют через внешний API."""

from typing import Any
from typing import Dict
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from src.external_api import convert_to_rub

# ---------------------------------------------------------------------------
# Фикстуры
# ---------------------------------------------------------------------------


@pytest.fixture
def rub_transaction() -> Dict[str, Any]:
    """Транзакция в рублях."""
    return {
        "operationAmount": {
            "amount": "31957.58",
            "currency": {"name": "руб.", "code": "RUB"},
        }
    }


@pytest.fixture
def usd_transaction() -> Dict[str, Any]:
    """Транзакция в долларах."""
    return {
        "operationAmount": {
            "amount": "100.00",
            "currency": {"name": "USD", "code": "USD"},
        }
    }


@pytest.fixture
def eur_transaction() -> Dict[str, Any]:
    """Транзакция в евро."""
    return {
        "operationAmount": {
            "amount": "250.50",
            "currency": {"name": "EUR", "code": "EUR"},
        }
    }


@pytest.fixture
def unsupported_transaction() -> Dict[str, Any]:
    """Транзакция в неподдерживаемой валюте."""
    return {
        "operationAmount": {
            "amount": "500.00",
            "currency": {"name": "GBP", "code": "GBP"},
        }
    }


# ---------------------------------------------------------------------------
# Тесты: транзакции в рублях (без вызова API)
# ---------------------------------------------------------------------------


class TestConvertToRubRUB:
    """Если валюта — RUB, API не вызывается, сумма возвращается как есть."""

    def test_rub_returns_amount(self, rub_transaction: Dict[str, Any]) -> None:
        """Рублёвая транзакция возвращает сумму без конвертации."""
        result = convert_to_rub(rub_transaction)
        assert result == 31957.58

    def test_rub_returns_float(self, rub_transaction: Dict[str, Any]) -> None:
        """Результат — float."""
        result = convert_to_rub(rub_transaction)
        assert isinstance(result, float)

    @patch("src.external_api.requests.get")
    def test_rub_does_not_call_api(self, mock_get: MagicMock, rub_transaction: Dict[str, Any]) -> None:
        """При валюте RUB запрос к API не отправляется."""
        convert_to_rub(rub_transaction)
        mock_get.assert_not_called()

    @pytest.mark.parametrize(
        "amount_str, expected",
        [
            ("0", 0.0),
            ("0.01", 0.01),
            ("999999.99", 999999.99),
        ],
    )
    def test_rub_various_amounts(self, amount_str: str, expected: float) -> None:
        """Разные суммы в RUB корректно конвертируются в float."""
        txn: Dict[str, Any] = {
            "operationAmount": {
                "amount": amount_str,
                "currency": {"name": "руб.", "code": "RUB"},
            }
        }
        assert convert_to_rub(txn) == expected


# ---------------------------------------------------------------------------
# Тесты: конвертация USD → RUB (с моком API)
# ---------------------------------------------------------------------------


class TestConvertToRubUSD:
    """Конвертация из долларов в рубли через замоканный API."""

    @patch("src.external_api.requests.get")
    def test_usd_calls_api(self, mock_get: MagicMock, usd_transaction: Dict[str, Any]) -> None:
        """Для USD отправляется GET-запрос к API."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": 8500.0}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        convert_to_rub(usd_transaction)
        mock_get.assert_called_once()

    @patch("src.external_api.requests.get")
    def test_usd_returns_converted_amount(self, mock_get: MagicMock, usd_transaction: Dict[str, Any]) -> None:
        """Возвращается сконвертированная сумма из ответа API."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": 8500.0}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = convert_to_rub(usd_transaction)
        assert result == 8500.0

    @patch("src.external_api.requests.get")
    def test_usd_api_params(self, mock_get: MagicMock, usd_transaction: Dict[str, Any]) -> None:
        """Проверяем, что API вызывается с правильными параметрами."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": 8500.0}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        convert_to_rub(usd_transaction)

        call_kwargs = mock_get.call_args
        assert call_kwargs[1]["params"]["from"] == "USD"
        assert call_kwargs[1]["params"]["to"] == "RUB"
        assert call_kwargs[1]["params"]["amount"] == 100.0


# ---------------------------------------------------------------------------
# Тесты: конвертация EUR → RUB (с моком API)
# ---------------------------------------------------------------------------


class TestConvertToRubEUR:
    """Конвертация из евро в рубли через замоканный API."""

    @patch("src.external_api.requests.get")
    def test_eur_returns_converted_amount(self, mock_get: MagicMock, eur_transaction: Dict[str, Any]) -> None:
        """EUR конвертируется корректно."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": 25050.0}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = convert_to_rub(eur_transaction)
        assert result == 25050.0

    @patch("src.external_api.requests.get")
    def test_eur_api_params(self, mock_get: MagicMock, eur_transaction: Dict[str, Any]) -> None:
        """EUR-запрос передаёт правильные параметры в API."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": 25050.0}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        convert_to_rub(eur_transaction)

        call_kwargs = mock_get.call_args
        assert call_kwargs[1]["params"]["from"] == "EUR"
        assert call_kwargs[1]["params"]["to"] == "RUB"
        assert call_kwargs[1]["params"]["amount"] == 250.5


# ---------------------------------------------------------------------------
# Тесты: неподдерживаемая валюта
# ---------------------------------------------------------------------------


class TestConvertToRubUnsupported:
    """Неподдерживаемая валюта вызывает ValueError."""

    def test_unsupported_currency_raises(self, unsupported_transaction: Dict[str, Any]) -> None:
        """GBP → ValueError."""
        with pytest.raises(ValueError, match="Неподдерживаемая валюта: GBP"):
            convert_to_rub(unsupported_transaction)

    @pytest.mark.parametrize("code", ["JPY", "CNY", "BTC", "XYZ"])
    def test_various_unsupported_currencies(self, code: str) -> None:
        """Разные неподдерживаемые коды валют → ValueError."""
        txn: Dict[str, Any] = {
            "operationAmount": {
                "amount": "100",
                "currency": {"name": code, "code": code},
            }
        }
        with pytest.raises(ValueError, match=f"Неподдерживаемая валюта: {code}"):
            convert_to_rub(txn)

    @patch("src.external_api.requests.get")
    def test_unsupported_does_not_call_api(self, mock_get: MagicMock, unsupported_transaction: Dict[str, Any]) -> None:
        """При неподдерживаемой валюте API не вызывается."""
        with pytest.raises(ValueError):
            convert_to_rub(unsupported_transaction)
        mock_get.assert_not_called()


# ---------------------------------------------------------------------------
# Тесты: ошибки API
# ---------------------------------------------------------------------------


class TestConvertToRubAPIErrors:
    """Обработка ошибок при обращении к API."""

    @patch("src.external_api.requests.get")
    def test_api_http_error(self, mock_get: MagicMock, usd_transaction: Dict[str, Any]) -> None:
        """HTTP-ошибка (raise_for_status) пробрасывается наружу."""
        import requests

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("401 Unauthorized")
        mock_get.return_value = mock_response

        with pytest.raises(requests.HTTPError):
            convert_to_rub(usd_transaction)

    @patch("src.external_api.requests.get")
    def test_api_connection_error(self, mock_get: MagicMock, usd_transaction: Dict[str, Any]) -> None:
        """ConnectionError при запросе пробрасывается наружу."""
        import requests

        mock_get.side_effect = requests.ConnectionError("Network unreachable")

        with pytest.raises(requests.ConnectionError):
            convert_to_rub(usd_transaction)

    @patch("src.external_api.requests.get")
    def test_api_timeout(self, mock_get: MagicMock, usd_transaction: Dict[str, Any]) -> None:
        """Timeout при запросе пробрасывается наружу."""
        import requests

        mock_get.side_effect = requests.Timeout("Request timed out")

        with pytest.raises(requests.Timeout):
            convert_to_rub(usd_transaction)

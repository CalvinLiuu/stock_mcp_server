"""Stake Australia trading integration for the MCP server.

This module focuses on enabling authenticated users to forward trading
instructions to the unofficial Stake (Australia) GraphQL endpoints. The
implementation purposely keeps the session handling light-weight and avoids
persisting credentials unless the caller explicitly requests it. The tools are
designed to be flexible so that advanced users can supply their own GraphQL
documents when Stake introduces breaking changes.

⚠️  Stake does not provide an officially supported public API. The helpers in
this module mirror the requests that the web trading interface performs. Users
must supply valid authentication tokens that they obtained through the normal
Stake login experience. The functions in this file do **not** bypass security
mechanisms and will only work for accounts that already have an active trading
session.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional

import requests
from mcp.server.fastmcp import FastMCP

# File used for optional credential persistence (disabled by default).
STAKE_SESSION_FILE = os.path.join(os.path.dirname(__file__), ".stake_session.json")


@dataclass
class StakeSessionConfig:
    """In-memory representation of the currently active Stake session."""

    api_url: str
    account_id: str
    access_token: str
    refresh_token: Optional[str] = None
    graphql_path: Optional[str] = None
    extra_headers: Dict[str, str] = field(default_factory=dict)
    token_expiry: Optional[float] = None

    def resolved_url(self) -> str:
        """Return the full URL used for GraphQL calls."""

        if self.graphql_path:
            if self.graphql_path.startswith("http://") or self.graphql_path.startswith("https://"):
                return self.graphql_path
            return f"{self.api_url.rstrip('/')}/{self.graphql_path.lstrip('/')}"
        return self.api_url

    def sanitized(self) -> Dict[str, Any]:
        """Return a redacted version of the configuration for user display."""

        data = asdict(self)
        data["access_token"] = "***redacted***"
        if data.get("refresh_token"):
            data["refresh_token"] = "***redacted***"
        return data


class StakeSessionManager:
    """Utility that loads, stores, and validates Stake session data."""

    def __init__(self) -> None:
        self._config: Optional[StakeSessionConfig] = None
        self._load_from_env()
        if not self._config:
            self._load_from_disk()

    def _load_from_env(self) -> None:
        api_url = os.environ.get("STAKE_API_URL")
        account_id = os.environ.get("STAKE_ACCOUNT_ID")
        access_token = os.environ.get("STAKE_ACCESS_TOKEN")
        if api_url and account_id and access_token:
            refresh_token = os.environ.get("STAKE_REFRESH_TOKEN")
            graphql_path = os.environ.get("STAKE_GRAPHQL_PATH")
            extra_headers: Dict[str, str] = {}
            extra_headers_env = os.environ.get("STAKE_EXTRA_HEADERS")
            if extra_headers_env:
                try:
                    extra_headers = json.loads(extra_headers_env)
                except json.JSONDecodeError:
                    extra_headers = {}
            expiry_env = os.environ.get("STAKE_TOKEN_EXPIRY")
            expiry_value: Optional[float] = None
            if expiry_env:
                try:
                    expiry_value = float(expiry_env)
                except ValueError:
                    expiry_value = None
            self._config = StakeSessionConfig(
                api_url=api_url,
                account_id=account_id,
                access_token=access_token,
                refresh_token=refresh_token,
                graphql_path=graphql_path,
                extra_headers=extra_headers,
                token_expiry=expiry_value,
            )

    def _load_from_disk(self) -> None:
        if os.path.exists(STAKE_SESSION_FILE):
            try:
                with open(STAKE_SESSION_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._config = StakeSessionConfig(
                    api_url=data["api_url"],
                    account_id=data["account_id"],
                    access_token=data["access_token"],
                    refresh_token=data.get("refresh_token"),
                    graphql_path=data.get("graphql_path"),
                    extra_headers=data.get("extra_headers", {}),
                    token_expiry=data.get("token_expiry"),
                )
            except (OSError, KeyError, json.JSONDecodeError):
                self._config = None

    def update_config(
        self,
        *,
        api_url: str,
        account_id: str,
        access_token: str,
        refresh_token: Optional[str] = None,
        graphql_path: Optional[str] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        token_expiry: Optional[float] = None,
        persist: bool = False,
    ) -> None:
        self._config = StakeSessionConfig(
            api_url=api_url,
            account_id=account_id,
            access_token=access_token,
            refresh_token=refresh_token,
            graphql_path=graphql_path,
            extra_headers=extra_headers or {},
            token_expiry=token_expiry,
        )
        if persist:
            self._persist()
        else:
            self._delete_persisted()

    def clear(self) -> None:
        self._config = None
        self._delete_persisted()

    def _persist(self) -> None:
        if not self._config:
            return
        data = asdict(self._config)
        try:
            with open(STAKE_SESSION_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except OSError:
            pass

    def _delete_persisted(self) -> None:
        if os.path.exists(STAKE_SESSION_FILE):
            try:
                os.remove(STAKE_SESSION_FILE)
            except OSError:
                pass

    def require_config(self) -> StakeSessionConfig:
        if not self._config:
            raise ValueError(
                "Stake session is not configured. Call 'configure_stake_connection' "
                "with valid credentials first."
            )
        if self._config.token_expiry and self._config.token_expiry < time.time():
            raise ValueError(
                "Stored Stake access token is expired. Refresh the token and run "
                "'configure_stake_connection' again."
            )
        return self._config

    def current_config(self) -> Optional[StakeSessionConfig]:
        return self._config


class StakeTradingClient:
    """Thin GraphQL client for Stake's trading endpoints."""

    def __init__(self, config: StakeSessionConfig) -> None:
        self._config = config
        self._session = requests.Session()

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self._config.access_token}",
            "Content-Type": "application/json",
        }
        headers.update(self._config.extra_headers)
        return headers

    def execute(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {"query": query, "variables": variables or {}}
        response = self._session.post(
            self._config.resolved_url(),
            json=payload,
            headers=self._headers(),
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        if "errors" in data:
            return {"errors": data["errors"], "data": data.get("data")}
        return data.get("data", data)

    def place_order(
        self,
        *,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str,
        time_in_force: str,
        outside_regular_hours: bool = False,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
    ) -> Dict[str, Any]:
        mutation = """
        mutation PlaceOrder($input: PlaceOrderInput!) {
          placeOrder(input: $input) {
            order {
              id
              status
              symbol
              side
              orderType
              timeInForce
              quantity
              limitPrice
              stopPrice
              submittedAt
            }
          }
        }
        """
        order_input: Dict[str, Any] = {
            "accountId": self._config.account_id,
            "symbol": symbol.upper(),
            "side": side.upper(),
            "quantity": quantity,
            "orderType": order_type.upper(),
            "timeInForce": time_in_force.upper(),
            "outsideRegularHours": outside_regular_hours,
        }
        if limit_price is not None:
            order_input["limitPrice"] = limit_price
        if stop_price is not None:
            order_input["stopPrice"] = stop_price
        variables = {"input": order_input}
        return self.execute(mutation, variables)

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        mutation = """
        mutation CancelOrder($input: CancelOrderInput!) {
          cancelOrder(input: $input) {
            order {
              id
              status
              symbol
            }
          }
        }
        """
        variables = {"input": {"accountId": self._config.account_id, "orderId": order_id}}
        return self.execute(mutation, variables)

    def list_orders(self, status_filter: Optional[str] = None) -> Dict[str, Any]:
        query = """
        query Orders($accountId: ID!, $status: OrderStatus) {
          orders(accountId: $accountId, status: $status) {
            id
            symbol
            side
            orderType
            status
            quantity
            limitPrice
            stopPrice
            submittedAt
          }
        }
        """
        variables: Dict[str, Any] = {"accountId": self._config.account_id}
        if status_filter:
            variables["status"] = status_filter
        return self.execute(query, variables)


def register_stake_tools(mcp: FastMCP) -> None:
    """Register Stake trading helpers with the MCP server."""

    session_manager = StakeSessionManager()

    @mcp.tool()
    def configure_stake_connection(
        api_url: str,
        account_id: str,
        access_token: str,
        refresh_token: Optional[str] = None,
        graphql_path: Optional[str] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        token_expiry: Optional[float] = None,
        persist: bool = False,
    ) -> str:
        """Configure the Stake trading session.

        Args:
            api_url: Base URL for Stake's API (e.g. "https://global-prd-api.stake.com").
            account_id: Internal Stake account identifier (UUID style string).
            access_token: Bearer token captured from a logged-in Stake session.
            refresh_token: Optional refresh token, stored only when persistence is enabled.
            graphql_path: Optional path appended to ``api_url`` (defaults to ``/graphql``).
            extra_headers: Additional HTTP headers required by Stake (e.g. ``{"x-client": "web"}``).
            token_expiry: Optional epoch timestamp for automatic expiry validation.
            persist: When ``True`` the credentials are saved to ``.stake_session.json``.
        """

        session_manager.update_config(
            api_url=api_url,
            account_id=account_id,
            access_token=access_token,
            refresh_token=refresh_token,
            graphql_path=graphql_path,
            extra_headers=extra_headers,
            token_expiry=token_expiry,
            persist=persist,
        )
        return (
            "Stake connection updated. The credentials are kept in memory"
            " and will persist across restarts only if `persist=True`."
        )

    @mcp.tool()
    def stake_connection_status() -> Dict[str, Any]:
        """Return the currently loaded Stake connection details without secrets."""

        config = session_manager.current_config()
        if not config:
            return {"configured": False}
        return {"configured": True, "details": config.sanitized()}

    @mcp.tool()
    def clear_stake_connection() -> str:
        """Remove any cached Stake credentials."""

        session_manager.clear()
        return "Stake connection cleared and any persisted credentials deleted."

    @mcp.tool()
    def stake_execute_graphql(query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a raw GraphQL document against Stake's API using stored credentials."""

        config = session_manager.require_config()
        client = StakeTradingClient(config)
        try:
            return client.execute(query, variables)
        except requests.exceptions.RequestException as exc:
            return {"error": str(exc)}

    @mcp.tool()
    def stake_place_order(
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "MARKET",
        time_in_force: str = "DAY",
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        outside_regular_hours: bool = False,
    ) -> Dict[str, Any]:
        """Submit an order through Stake using an authenticated session."""

        normalized_side = side.upper()
        if normalized_side not in {"BUY", "SELL"}:
            return {"error": "Order side must be either 'BUY' or 'SELL'."}
        config = session_manager.require_config()
        client = StakeTradingClient(config)
        try:
            return client.place_order(
                symbol=symbol,
                side=normalized_side,
                quantity=quantity,
                order_type=order_type,
                time_in_force=time_in_force,
                limit_price=limit_price,
                stop_price=stop_price,
                outside_regular_hours=outside_regular_hours,
            )
        except requests.exceptions.RequestException as exc:
            return {"error": str(exc)}

    @mcp.tool()
    def stake_cancel_order(order_id: str) -> Dict[str, Any]:
        """Attempt to cancel an existing Stake order."""

        config = session_manager.require_config()
        client = StakeTradingClient(config)
        try:
            return client.cancel_order(order_id)
        except requests.exceptions.RequestException as exc:
            return {"error": str(exc)}

    @mcp.tool()
    def stake_list_orders(status_filter: Optional[str] = None) -> Dict[str, Any]:
        """List orders for the configured Stake account."""

        config = session_manager.require_config()
        client = StakeTradingClient(config)
        try:
            return client.list_orders(status_filter)
        except requests.exceptions.RequestException as exc:
            return {"error": str(exc)}


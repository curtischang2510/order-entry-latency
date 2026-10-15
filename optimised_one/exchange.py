from itertools import count
from typing import Any

from hyperliquid.exchange import Exchange
from hyperliquid.utils.constants import MAINNET_API_URL
from hyperliquid.utils.signing import (
    Grouping,
    OrderRequest,
    OrderWire,
    get_timestamp_ms,
    order_request_to_order_wire,
    order_wires_to_order_action,
    sign_l1_action,
)
from hyperliquid.utils.types import BuilderInfo


class NonceExchange(Exchange):
    """Assign a distinct, increasing nonce to each order in this process."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._nonces = count(get_timestamp_ms())
        super().__init__(*args, **kwargs)

    def bulk_orders(
        self,
        order_requests: list[OrderRequest],
        builder: BuilderInfo | None = None,
        grouping: Grouping = "na",
    ) -> Any:
        order_wires: list[OrderWire] = [
            order_request_to_order_wire(order, self.info.name_to_asset(order["coin"]))
            for order in order_requests
        ]
        nonce = next(self._nonces)

        if builder:
            builder["b"] = builder["b"].lower()
        order_action = order_wires_to_order_action(order_wires, builder, grouping)

        signature = sign_l1_action(
            self.wallet,
            order_action,
            self.vault_address,
            nonce,
            self.expires_after,
            self.base_url == MAINNET_API_URL,
        )
        return self._post_action(order_action, signature, nonce)

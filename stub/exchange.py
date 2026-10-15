from typing import Any, override

from hyperliquid.exchange import Exchange


class StubExchange(Exchange):
    """Build and sign orders without submitting them over HTTP."""

    @override
    def post(self, url_path: str, payload: Any = None) -> Any:
        return None

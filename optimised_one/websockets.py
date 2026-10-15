import json
import logging
import sys
from pathlib import Path

import websocket
from hyperliquid.exchange import Exchange
from hyperliquid.utils.signing import Account
from hyperliquid.utils import constants

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config import Config  # noqa: E402

logger = logging.getLogger(__name__)
LOG_FILE = Path(__file__).with_name("orders.log")
TESTNET_WEBSOCKET_URL = "wss://api.hyperliquid-testnet.xyz/ws"

NUM_TICKS = 100


"""
Order entry latency
- Use the Hyperliquid Python SDK to insert an order to Hyperliquid Testnet
- Trace the processing latency of your order at various relevant intermediate steps
- Take measures to reduce this latency as much as possible
- Show the progress you made in reducing latency as a result of the various changes you implemented
"""

class WebSocketExchange(Exchange):
    """Use the SDK to prepare and sign orders, then send them over WebSocket."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ws = websocket.create_connection(TESTNET_WEBSOCKET_URL, timeout=self.timeout)
        self.request_id = 0

    def _post_action(self, action, signature, nonce):
        self.request_id += 1
        request_id = self.request_id
        payload = {
            "action": action,
            "nonce": nonce,
            "signature": signature,
            "vaultAddress": self.vault_address if action["type"] not in ("usdClassTransfer", "sendAsset") else None,
            "expiresAfter": self.expires_after,
        }
        self.ws.send(json.dumps({
            "method": "post",
            "id": request_id,
            "request": {"type": "action", "payload": payload},
        }))
        while True:
            message = json.loads(self.ws.recv())
            if message.get("channel") != "post":
                continue
            data = message["data"]
            if data.get("id") != request_id:
                continue
            response = data["response"]
            if response.get("type") != "action":
                raise RuntimeError(f"WebSocket order request failed: {response.get('payload')}")
            return response["payload"]


def main() -> None:
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    
    config = Config.from_yaml(PROJECT_ROOT / "config.yaml")
    wallet = Account.from_key(config.private_key)
    exchange = WebSocketExchange(
        wallet,
        base_url=constants.TESTNET_API_URL,
        account_address=config.account_address,
        timeout=5
    )
    # account_value = float(exchange.info.user_state(config.account_address)["marginSummary"]["accountValue"])
    try:
        for i in range(NUM_TICKS):
            # if planning engine returns true
            if i % 2 == 0:
                result = exchange.order(
                    config.coin,
                    True,
                    config.size,
                    config.price,
                    {"limit": {"tif": "Gtc"}},
                )
                logger.info("Order result at tick %d: %s", i, result)
    finally:
        exchange.ws.close()


if __name__ == "__main__":
    main()

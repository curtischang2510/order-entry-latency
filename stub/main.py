import logging
import sys
from pathlib import Path
import time

from hyperliquid.utils.signing import Account
from hyperliquid.utils import constants

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config import Config  # noqa: E402
from decorator import get_latency  # noqa: E402
from stub.exchange import StubExchange  # noqa: E402

logger = logging.getLogger(__name__)
LOG_FILE = Path(__file__).with_name("orders.log")

NUM_TICKS = 100


"""
Order entry latency
- Use the Hyperliquid Python SDK to insert an order to Hyperliquid Testnet
- Trace the processing latency of your order at various relevant intermediate steps
- Take measures to reduce this latency as much as possible
- Show the progress you made in reducing latency as a result of the various changes you implemented
"""

def main() -> None:
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    
    config = Config.from_yaml(PROJECT_ROOT / "config.yaml")
    wallet = Account.from_key(config.private_key)
    exchange = StubExchange(
        wallet,
        base_url=constants.TESTNET_API_URL,
        account_address=config.account_address,
        timeout=5
    )
    # account_value = float(exchange.info.user_state(config.account_address)["marginSummary"]["accountValue"])
    for i in range(NUM_TICKS):
        # if planning engine returns true
        if i % 2 == 0:
            time.sleep(0.8)
            start = time.perf_counter()
            result = exchange.order(
                config.coin, 
                True,
                config.size,
                config.price,
                {"limit": {"tif": "Gtc"}},
            )
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.info("Stub order result at tick %d: %s", i, result)
            logger.info("Order latency at tick %d: %s", i, elapsed_ms)


if __name__ == "__main__":
    main()

import asyncio
import logging
import sys
from pathlib import Path

from hyperliquid.exchange import Exchange
from hyperliquid.utils.signing import Account
from hyperliquid.utils import constants

from optimised_one.async_queue import AsyncOrderQueue, OrderJob

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config import Config  # noqa: E402

LOG_FILE = Path(__file__).with_name("orders.log")
NUM_TICKS = 100


async def main() -> None:
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    
    config = Config.from_yaml(PROJECT_ROOT / "config.yaml")
    wallet = Account.from_key(config.private_key)
    exchange = Exchange(
        wallet,
        base_url=constants.TESTNET_API_URL,
        account_address=config.account_address,
        timeout=5
    )
    # account_value = float(exchange.info.user_state(config.account_address)["marginSummary"]["accountValue"])
    async_order_queue = AsyncOrderQueue(exchange)
    for i in range(NUM_TICKS):
        # if planning engine returns true
        if i % 2 == 0:
            job = OrderJob(config.coin, config.size, config.price, asyncio.Future())
            await async_order_queue.append(job)
    await async_order_queue.join()

if __name__ == "__main__":
    asyncio.run(main())

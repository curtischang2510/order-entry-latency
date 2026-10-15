"""Cancel this account's open testnet orders whose IDs appear in an order log."""

import argparse
import ast
import json
from pathlib import Path

from eth_account import Account
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants

from config import Config


PROJECT_ROOT = Path(__file__).resolve().parent


def resting_order_ids(log_file: Path) -> set[int]:
    order_ids: set[int] = set()
    with log_file.open(encoding="utf-8") as lines:
        for line in lines:
            _, marker, remainder = line.partition("Order result")
            if not marker:
                continue
            start = remainder.find("{")
            if start < 0:
                continue
            result_text = remainder[start:]
            try:
                result = ast.literal_eval(result_text)
            except (SyntaxError, ValueError):
                try:
                    result = json.loads(result_text)
                except json.JSONDecodeError:
                    continue
            if not isinstance(result, dict) or result.get("status") != "ok":
                continue
            response = result.get("response", {})
            if not isinstance(response, dict) or response.get("type") != "order":
                continue
            for status in response.get("data", {}).get("statuses", []):
                if isinstance(status, dict):
                    resting = status.get("resting")
                    if isinstance(resting, dict) and type(resting.get("oid")) is int:
                        order_ids.add(resting["oid"])
    return order_ids


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log_file", type=Path, help="Order log to read")
    parser.add_argument("--coin", help="Coin to cancel; defaults to the configured coin")
    parser.add_argument("--config", type=Path, default=PROJECT_ROOT / "config.yaml")
    args = parser.parse_args()

    try:
        logged_ids = resting_order_ids(args.log_file)
    except OSError as exc:
        parser.error(str(exc))
    if not logged_ids:
        print("No resting order IDs found in the log.")
        return

    config = Config.from_yaml(args.config)
    coin = args.coin or config.coin
    exchange = Exchange(
        Account.from_key(config.private_key),
        base_url=constants.TESTNET_API_URL,
        account_address=config.account_address,
        timeout=10,
    )
    open_ids = {
        order["oid"]
        for order in exchange.info.open_orders(config.account_address)
        if order.get("coin") == coin
    }
    to_cancel = sorted(logged_ids & open_ids)
    print(f"Found {len(to_cancel)} open {coin} order(s) from the log.")
    for oid in to_cancel:
        result = exchange.cancel(coin, oid)
        print(f"Cancel {coin} order {oid}: {result}")


if __name__ == "__main__":
    main()

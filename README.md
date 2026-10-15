# Order entry latency

Baseline using the Hyperliquid Python SDK to place one **testnet** GTC buy limit order.
The installed SDK contains the importable `hyperliquid` package but does not include
the repository's `examples/` directory. This implementation follows the upstream
[`basic_order.py`](https://github.com/hyperliquid-dex/hyperliquid-python-sdk/blob/master/examples/basic_order.py)
example.

Set a funded testnet account address and an authorized testnet API wallet's
private key in `config.yaml`. The account address is the main account, not the
API wallet address. Keep `config.yaml` private; it is ignored by Git.
Before submitting an order, the runner checks that this address has testnet
perpetual equity or USDC collateral in unified account mode. The key in `private_key` must belong to that account or to
an API wallet authorized by that account on testnet.

```yaml
account_address: "0xYOUR_MAIN_ACCOUNT_ADDRESS"
private_key: "0xYOUR_TESTNET_API_WALLET_PRIVATE_KEY"
order:
  coin: ETH
  size: auto
  price: 1100.0
```

Use a deliberately passive price so the order rests and can be cancelled.
Run from the project root:

```sh
uv run order-entry-latency
```

`config.py` is shared at the repository root. A future variant in a subfolder can
use `from config import Config` and be run as a module from the root, for example
`uv run python -m variant_name.main`.

The command computes the smallest ETH size whose value at the limit price is at
least Hyperliquid's $10 perpetual-order minimum, rounded up to ETH's size
increment from testnet metadata. This size changes with the price and asset.
Set `order.size` to `auto` or `null` for the calculated minimum, or to a number
for a larger amount. `--minimum-size` uses the calculated minimum for one run.
`--coin`, `--size`, `--price`, and `--config` can override
the YAML values. A price far from the current market may be rejected by the
exchange; choose a passive but valid testnet price.
Each run sends one order and cancels it if it rests. A resting order can reserve
margin while open; if it fills before cancellation, it creates a real testnet
position that this script does not close.

The command prints JSON with setup time, SDK order preparation and signing time,
HTTP submission and response time, total `exchange.order()` time, the API response,
and a cancellation result when the order rests. Times use a monotonic clock and
are measured on the client. The HTTP segment includes request serialization,
network transit, server handling, and response parsing; it does not isolate those
components. Setup and cancellation are outside the order-entry total. Keep the
same coin, size, price policy, account, and environment when comparing later runs.

For orders recorded by `baseline/main.py`, cancel any that are still open with:

```sh
uv run python cancel_orders.py baseline/orders.log
```

Pass a different log path to inspect another variant's run. The cleanup script reads
lines containing `Order result` followed by a Python or JSON response. It only cancels
resting order IDs found in that log that are still open on the configured testnet
account. Use `--coin` if the logged orders used a different asset than `config.yaml`.

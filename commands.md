# Commands

Run these from the repository root. `baseline.main` and `optimised_one.main` place testnet orders. `stub.main` does not submit orders.

## Run the scripts

```sh
uv run python -m baseline.main
uv run python -m optimised_one.main
uv run python -m stub.main
```

Use the separate Python 3.13 environment for the CoinCurve signing comparison:

```sh
.venv-313/bin/python -m baseline.main
.venv-313/bin/python -m optimised_one.main
.venv-313/bin/python -m stub.main
```

Measure the total shell runtime, including startup:

```sh
time uv run python -m baseline.main
```

## Sampling profiler

Wall mode includes time spent waiting for network responses:

```sh
sudo -E uv run python -m profiling.sampling run \
  --heatmap -r 5khz -o baseline/heatmap -m baseline.main
```

CPU mode focuses on work done while the process is using the CPU:

```sh
sudo -E uv run python -m profiling.sampling run \
  --heatmap --mode cpu -r 5khz -o baseline/heatmap -m baseline.main
```

To profile another script, change both `-o baseline/heatmap` and `-m baseline.main` to that script's folder and module. For `optimised_one.main`, add `-a` to sample its worker threads.

## Network checks

Resolve the testnet API hostname:

```sh
dig +short api.hyperliquid-testnet.xyz
```

Send 20 ICMP pings to the resolved CDN address:

```sh
ping -c 20 api.hyperliquid-testnet.xyz
```

Trace TCP port 443 to the CDN. On macOS:

```sh
sudo traceroute -n -P TCP -p 443 api.hyperliquid-testnet.xyz
```

On Ubuntu:

```sh
sudo traceroute -n -T -p 443 api.hyperliquid-testnet.xyz
```

Time a POST to the testnet `/info` endpoint:

```sh
curl -sS -o /dev/null \
  -w 'ip %{remote_ip} | dns %{time_namelookup}s | connect %{time_connect}s | tls %{time_appconnect}s | first byte %{time_starttransfer}s | total %{time_total}s | status %{http_code}\n' \
  -H 'Content-Type: application/json' \
  -d '{"type":"meta"}' \
  https://api.hyperliquid-testnet.xyz/info
```

Curl's times are cumulative. Subtract `time_connect` from `time_appconnect` to get TLS handshake time.

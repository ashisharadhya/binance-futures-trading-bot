# Trading Bot — Binance Futures Testnet (USDT-M)

A small, structured CLI application that places MARKET and LIMIT orders on
Binance Futures Testnet, with input validation, logging, and error handling.

## Project Structure

```
trading_bot/
  bot/
    __init__.py
    client.py        # Binance client wrapper (auth, base URL, API calls)
    orders.py         # Order placement logic + CLI-facing output formatting
    validators.py      # Input validation, isolated from CLI parsing
    logging_config.py  # Rotating file + console logging setup
  cli.py               # CLI entry point (argparse)
  README.md
  requirements.txt
  trading_bot.log      # Created at runtime; contains all request/response/error logs
```

## Setup

### 1. Create a Futures Demo Trading API key

Binance renamed/relocated the old Futures Testnet: it's now called
**Demo Trading** and uses your regular Binance account (no separate
GitHub-based testnet account anymore). The underlying API is still fully
separate from your real balance — it only trades against simulated funds.

1. Log in at https://demo.binance.com with your normal Binance account
   (create a free account if you don't have one — no KYC required for this).
2. Go to **Account → API Management** (`demo.binance.com/en/my/settings/api-management`).
3. Click **Create API**, choose **System generated** (HMAC), give it a name.
4. Complete any verification step (email/2FA) Binance asks for.
5. Copy the **API Key** and **Secret Key** immediately — the Secret Key is
   only shown once.
6. Make sure **Enable Futures** is checked under API restrictions.

### 2. Install dependencies

```bash
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set your credentials

Recommended — environment variables (keeps keys out of shell history and code):

```bash
export BINANCE_TESTNET_API_KEY="your_api_key"
export BINANCE_TESTNET_API_SECRET="your_api_secret"
```

On Windows (PowerShell):
```powershell
$env:BINANCE_TESTNET_API_KEY="your_api_key"
$env:BINANCE_TESTNET_API_SECRET="your_api_secret"
```

Alternatively, pass `--api-key` / `--api-secret` directly on the command line.

## How to Run

### Market order

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

### Limit order

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 60000
```

### Sample output

```
--- Order Request ---
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.01
----------------------

--- Order Response ---
  Order ID     : 123456789
  Status       : FILLED
  Executed Qty : 0.01
  Avg Price    : 60123.40
-----------------------

SUCCESS: MARKET BUY order placed for BTCUSDT.
```

All requests, responses, and errors are also written to `trading_bot.log`
in the project root (rotates at 2MB, keeps 3 backups).

## Error Handling

The app validates all input before making any network call, and distinguishes
between three failure categories, each logged and reported clearly:

- **Invalid input** (e.g. bad symbol format, missing price on a LIMIT order,
  non-numeric quantity) — caught in `validators.py`, no API call is made.
- **Binance API errors** (e.g. invalid symbol, insufficient testnet balance,
  precision/lot-size errors, auth failure) — caught in `client.py` and
  surfaced with Binance's own error message.
- **Network errors** (timeouts, connection failures) — caught and reported
  without crashing the CLI.

In all failure cases the CLI exits with a non-zero status code and prints a
`FAILED:` message, so it can be scripted/tested reliably.

## Assumptions

- Quantity and price precision/step-size rules (e.g. BTCUSDT requires
  quantity in multiples of 0.001) are enforced by Binance itself; the app
  surfaces those rejections rather than re-implementing exchange filters
  client-side. For a production version, fetching `exchangeInfo` and
  validating against `LOT_SIZE`/`PRICE_FILTER` client-side would be a
  natural next step.
- LIMIT orders are submitted with `timeInForce=GTC` (Good-Til-Cancelled),
  since the task didn't specify a different policy.
- Only USDT-M Futures paper trading is targeted. The task brief specified
  `testnet.binancefuture.com`, but Binance has since retired that domain in
  favor of "Demo Trading" served from `demo-fapi.binance.com`; this app
  targets the current live endpoint so it actually works today.
- API credentials are never logged, even at DEBUG level.

## Possible Extensions (not implemented)

- STOP-LIMIT / OCO order support
- Interactive CLI prompts (e.g. via `Click` or `questionary`) as an
  alternative to pure `argparse` flags
- Automated tests for `validators.py` using `pytest`

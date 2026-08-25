# Binance Portfolio Tracker

## Purpose

This project watches Binance copy-trading lead portfolios, stores trades in a single Excel file, and sends Telegram notifications when new trades appear.

The project now supports multiple `portfolioId`s. New portfolio IDs can be added or removed through Telegram commands while the app is running.

## Current Behavior

- Polls Telegram for bot commands
- Loads tracked portfolio IDs from `portfolio_config.json`
- Fetches recent Binance trades for each tracked portfolio
- Deduplicates trades before saving
- Writes all portfolios into one Excel file: `binance_trades.xlsx`
- Sends Telegram notifications only for newly added trades

## Main Files

- `main.py`
  Runs the main loop. Polls Telegram, reloads config, and triggers Binance fetch cycles.

- `config_store.py`
  Stores tracked portfolios in `portfolio_config.json`.

- `portfolio_tracker.py`
  Creates and manages one tracker per `portfolioId`.

- `binance_api.py`
  Calls the Binance endpoint for portfolio order history.

- `excel_manager.py`
  Deduplicates and writes all trades into one Excel file.

- `telegram_notifier.py`
  Sends Telegram messages and polls Telegram updates.

- `telegram_commands.py`
  Parses Telegram bot commands like `/add`, `/remove`, `/list`, `/setlabel`.

- `test_extractor.py`
  Generates fake trades for local Excel/notification testing.

## Data Model

All trades are stored in one Excel file. Each row includes:

- `portfolioId`
- `portfolioLabel`
- `symbol`
- `orderTime`
- `baseAsset`
- `quoteAsset`
- `side`
- `type`
- `positionSide`
- `executedQty`
- `avgPrice`
- `totalPnl`
- `orderUpdateTime`

This allows multiple portfolios to share one file while still being filterable in Excel.

## Runtime Flow

1. Start app with `python3 main.py`
2. App loads `portfolio_config.json`
3. App polls Telegram for commands every few seconds
4. If command changes portfolio config, next loop reloads it automatically
5. App fetches Binance trades for all tracked portfolio IDs
6. New trades are appended to `binance_trades.xlsx`
7. Notification is sent to Telegram for newly detected trades

No restart is needed when adding or removing portfolio IDs from Telegram.

## Telegram Commands

Supported commands:

- `/help`
- `/list`
- `/add <portfolio_id> [label]`
- `/remove <portfolio_id>`
- `/setlabel <portfolio_id> <label>`

Examples:

```text
/add 4649626508338132480 Main
/add 9876543210987654321 Alt
/list
/setlabel 4649626508338132480 MainAccount
/remove 9876543210987654321
```

## Environment Variables

Create a `.env` file with:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
DEFAULT_PORTFOLIO_ID=4649626508338132480
FETCH_INTERVAL_SECONDS=60
TELEGRAM_POLL_SECONDS=5
EXCEL_FILENAME=binance_trades.xlsx
```

Notes:

- `TELEGRAM_BOT_TOKEN` is required
- `TELEGRAM_CHAT_ID` is used for outgoing trade notifications
- incoming commands are read through Telegram `getUpdates`
- `DEFAULT_PORTFOLIO_ID` is inserted only when config is empty

## Setup

Recommended setup uses a fresh virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install "numpy<2" -r requirements.txt
```

Then run:

```bash
python3 main.py
```

For faster manual testing:

```bash
FETCH_INTERVAL_SECONDS=10 TELEGRAM_POLL_SECONDS=2 python3 main.py
```

## Local Test Mode

To test Excel writing and Telegram notifications without Binance:

```bash
python3 test_extractor.py
```

This writes fake trades into `test_binance_trades.xlsx`.

## Config File

Tracked portfolios are stored in `portfolio_config.json`.

Current shape:

```json
{
  "portfolios": [
    {
      "portfolio_id": "4649626508338132480",
      "label": "Main",
      "enabled": true
    }
  ]
}
```

## Known Caveats

- Binance may change request validation or anti-bot behavior. If valid portfolio IDs stop returning data, inspect `binance_api.py` first.
- The app currently trusts any Telegram user/chat that can reach the bot command path. There is no admin allowlist yet.
- All portfolios share one Excel format and one output file by design.
- Trade deduplication uses:
  - `orderTime`
  - `symbol`
  - `side`
  - `executedQty`

## Suggested Next Improvements

- Add Telegram user/chat allowlist for admin commands
- Add `/ping` or `/status`
- Add logging to a file
- Add retry/backoff around Binance failures
- Add tests for config store and Excel deduplication
# number_sepration

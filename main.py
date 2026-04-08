import logging
import os
import time

from binance_api import BinanceAPI
from config_store import PortfolioConfigStore
from portfolio_tracker import PortfolioTrackerManager
from telegram_commands import TelegramCommandProcessor
from telegram_notifier import TelegramNotifier


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

FETCH_INTERVAL_SECONDS = int(os.getenv("FETCH_INTERVAL_SECONDS", "60"))
TELEGRAM_POLL_SECONDS = int(os.getenv("TELEGRAM_POLL_SECONDS", "5"))
DEFAULT_PORTFOLIO_ID = os.getenv("DEFAULT_PORTFOLIO_ID", "4649626508338132480")
EXCEL_FILENAME = os.getenv("EXCEL_FILENAME", "binance_trades.xlsx")


def main():
    config_store = PortfolioConfigStore()
    config_store.ensure_default(DEFAULT_PORTFOLIO_ID)

    notifier = TelegramNotifier()
    api = BinanceAPI()
    tracker_manager = PortfolioTrackerManager(
        api=api,
        notifier=notifier,
        excel_filename=EXCEL_FILENAME,
    )
    command_processor = TelegramCommandProcessor(
        notifier=notifier,
        config_store=config_store,
    )

    next_fetch_at = 0.0
    logging.info(
        "Tracker started. Fetch interval=%ss, telegram poll interval=%ss",
        FETCH_INTERVAL_SECONDS,
        TELEGRAM_POLL_SECONDS,
    )

    try:
        while True:
            command_processor.process_pending_updates()
            tracker_manager.sync(config_store.list_portfolios())

            now = time.monotonic()
            if now >= next_fetch_at:
                tracker_manager.run_cycle()
                next_fetch_at = now + FETCH_INTERVAL_SECONDS

            time.sleep(TELEGRAM_POLL_SECONDS)
    except KeyboardInterrupt:
        logging.info("Exiting application...")


if __name__ == "__main__":
    main()

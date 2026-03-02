import time
import schedule
import logging
import datetime
from binance_api import BinanceAPI
from excel_manager import ExcelManager
from event_bus import bus

# Setup simple logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Configuration
PORTFOLIO_ID = "4649626508338132480"
FETCH_INTERVAL_MINUTES = 1

from telegram_notifier import telegram_bot

def on_new_trades_notification(trades):
    # This acts as a placeholder for a notification system
    # Because of the EventBus, this function is completely decoupled from the Excel formatting logic
    logging.info(f"NOTIFICATION: {len(trades)} new trades have been added to the system!")
    
    # Send the trades array to Telegram
    telegram_bot.format_and_send_trades(trades)

def fetch_job(api, excel_mgr):
    logging.info("Running scheduled data extraction...")
    
    # We want to fetch trades up to 'now', and starting from e.g., 2 days ago to be safe
    # Though we run every minute, fetching a larger window ensures no data missing if script offline
    end_time_ms = int(datetime.datetime.now().timestamp() * 1000)
    # 2 days in ms = 2 * 24 * 60 * 60 * 1000 = 172800000
    start_time_ms = end_time_ms - 172800000 
    
    trades = api.fetch_orders(start_time_ms, end_time_ms, page_size=100)
    
    if trades:
        # Publish to event bus for processing
        bus.publish("on_raw_trades_fetched", trades)

def main():
    api = BinanceAPI(PORTFOLIO_ID)
    excel_mgr = ExcelManager()
    
    # Subscribe systems to events
    bus.subscribe("on_raw_trades_fetched", excel_mgr.process_new_trades)
    bus.subscribe("on_new_trades_saved", on_new_trades_notification)
    
    # Run the job once immediately on startup
    fetch_job(api, excel_mgr)
    
    # Schedule the recurring job
    schedule.every(FETCH_INTERVAL_MINUTES).minutes.do(fetch_job, api, excel_mgr)
    
    logging.info(f"Scheduler started. Running every {FETCH_INTERVAL_MINUTES} minute(s). Press Ctrl+C to exit.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
            
    except KeyboardInterrupt:
        logging.info("Exiting application...")

if __name__ == "__main__":
    main()

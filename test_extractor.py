import time
import schedule
import logging
import datetime
import random
from excel_manager import ExcelManager
from event_bus import bus
from main import on_new_trades_notification

# Setup simple logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def fetch_fake_job(excel_mgr):
    logging.info("Generating fake trades for testing...")
    
    current_time_ms = int(datetime.datetime.now().timestamp() * 1000)
    
    # Generate 1 to 3 random new trades
    mock_trades = []
    num_trades = random.randint(1, 3)
    
    for _ in range(num_trades):
        # Random trade time within the last 10 seconds
        trade_time = current_time_ms - random.randint(0, 10000)
        symbol = random.choice(["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT"])
        side = random.choice(["BUY", "SELL"])
        qty = round(random.uniform(0.1, 5.0), 4)
        price = round(random.uniform(50, 70000), 2)
        
        trade = {
            "symbol": symbol,
            "baseAsset": symbol.replace("USDT", ""),
            "quoteAsset": "USDT",
            "side": side,
            "type": "MARKET",
            "positionSide": "BOTH",
            "executedQty": qty,
            "avgPrice": price,
            "totalPnl": round(random.uniform(-100, 500), 2),
            "orderUpdateTime": trade_time,
            "orderTime": trade_time
        }
        mock_trades.append(trade)
    
    # We will also pass a static trade every time to prove that deduplication ignores it!
    # Because it has the exact same orderTime, symbol, side, and executedQty
    static_trade = {
        "symbol": "STATIC_DEDUPE_TEST",
        "baseAsset": "STATIC",
        "quoteAsset": "USDT",
        "side": "BUY",
        "type": "MARKET",
        "positionSide": "BOTH",
        "executedQty": 100.0,
        "avgPrice": 1.0,
        "totalPnl": 0.0,
        # Give it a permanent fixed timestamp for testing
        "orderUpdateTime": 1772260354981, 
        "orderTime": 1772260354981 
    }
    mock_trades.append(static_trade)
    
    # Shuffle so the static trade isn't always at the end
    random.shuffle(mock_trades)
    
    # Publish to the event bus just like the real API would
    bus.publish("on_raw_trades_fetched", mock_trades)

def start_test():
    # Write to a separate test file so we don't pollute your real data
    excel_mgr = ExcelManager(filename="test_binance_trades.xlsx")
    
    # Subscribe systems to events
    bus.subscribe("on_raw_trades_fetched", excel_mgr.process_new_trades)
    bus.subscribe("on_new_trades_saved", on_new_trades_notification)
    
    # Run once immediately
    fetch_fake_job(excel_mgr)
    
    # In test mode, we'll run it every 10 seconds instead of 1 minute!
    schedule.every(10).seconds.do(fetch_fake_job, excel_mgr)
    
    logging.info("Test scheduler started. Generating fake trades every 10 seconds. Press Ctrl+C to exit.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
            
    except KeyboardInterrupt:
        logging.info("Exiting test application...")

if __name__ == "__main__":
    start_test()

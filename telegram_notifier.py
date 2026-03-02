import requests
import logging
import os
from dotenv import load_dotenv  # ← add this

load_dotenv()  # ← add this, loads .env file

class TelegramNotifier:
    def __init__(self, bot_token=None, chat_id=None):
        # REPLACE THESE WITH YOUR ACTUAL BOT TOKEN AND CHAT ID
        # You can get a Bot Token from BotFather on Telegram
        # You can get your Chat ID by messaging your bot and looking at https://api.telegram.org/bot<TOKEN>/getUpdates
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")  # ← change this
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")         # ← change this
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    def send_message(self, message):
        if self.bot_token == "YOUR_BOT_TOKEN_HERE" or self.chat_id == "YOUR_CHAT_ID_HERE":
            logging.warning("Telegram config not set! Message not sent: " + message.split('\n')[0])
            return

        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            logging.info("Telegram notification sent successfully.")
        except Exception as e:
            logging.error(f"Failed to send Telegram message: {e}")

    def format_and_send_trades(self, trades):
        """
        Formats a list of new trades and sends them via Telegram.
        """
        if not trades:
            return
            
        header = f"🚨 <b>{len(trades)} New Trades Detected!</b> 🚨\n\n"
        body = ""
        
        for trade in trades:
            # Emoji based on Side
            side_emoji = "🟢" if trade.get("side") == "BUY" else "🔴"
            
            body += (
                f"{side_emoji} <b>{trade.get('side')} {trade.get('symbol')}</b>\n"
                f"Amount: {trade.get('executedQty')} {trade.get('baseAsset')}\n"
                f"Price: {trade.get('avgPrice')}\n"
                f"Time: {trade.get('orderTime')}\n"
                f"-----------------------\n"
            )
            
        full_message = header + body
        self.send_message(full_message)

# Global singleton
telegram_bot = TelegramNotifier()
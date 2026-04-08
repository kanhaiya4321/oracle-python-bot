import requests
import logging
import os
from dotenv import load_dotenv

load_dotenv()

class TelegramNotifier:
    def __init__(self, bot_token=None, chat_id=None):
        # Reads credentials from .env file automatically
        # .env should contain: TELEGRAM_BOT_TOKEN=... and TELEGRAM_CHAT_ID=...
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID_HERE")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    def is_configured(self):
        return self.bot_token != "YOUR_BOT_TOKEN_HERE"

    def send_message(self, message, chat_id=None, parse_mode="HTML"):
        target_chat_id = chat_id or self.chat_id
        if self.bot_token == "YOUR_BOT_TOKEN_HERE" or not target_chat_id or target_chat_id == "YOUR_CHAT_ID_HERE":
            logging.warning("Telegram config not set! Message not sent: " + message.split('\n')[0])
            return

        payload = {
            "chat_id": target_chat_id,
            "text": message,
        }
        if parse_mode:
            payload["parse_mode"] = parse_mode
        
        try:
            response = requests.post(f"{self.base_url}/sendMessage", json=payload, timeout=30)
            response.raise_for_status()
            logging.info("Telegram notification sent successfully.")
        except Exception as e:
            response_text = ""
            if hasattr(e, "response") and e.response is not None:
                response_text = f" | response={e.response.text}"
            logging.error(f"Failed to send Telegram message: {e}{response_text}")

    def get_updates(self, offset=None, timeout=10):
        if not self.is_configured():
            return []

        payload = {
            "timeout": timeout,
            "allowed_updates": ["message"],
        }
        if offset is not None:
            payload["offset"] = offset

        try:
            response = requests.get(f"{self.base_url}/getUpdates", params=payload, timeout=timeout + 5)
            response.raise_for_status()
            data = response.json()
            if data.get("ok"):
                return data.get("result", [])
            logging.error("Failed to get Telegram updates: %s", data)
            return []
        except Exception as exc:
            logging.error("Failed to poll Telegram updates: %s", exc)
            return []

    def format_and_send_trades(self, trades, portfolio_config=None):
        """
        Formats a list of new trades and sends them via Telegram.
        """
        if not trades:
            return

        portfolio_name = None
        if portfolio_config:
            portfolio_name = portfolio_config.get("label") or portfolio_config.get("portfolio_id")

        header_title = f"{len(trades)} New Trades Detected!"
        if portfolio_name:
            header_title = f"{header_title} [{portfolio_name}]"

        header = f"🚨 <b>{header_title}</b> 🚨\n\n"
        body = ""
        
        for trade in trades:
            # Emoji based on Side
            side_emoji = "🟢" if trade.get("side") == "BUY" else "🔴"
            
            body += (
                f"{side_emoji} <b>{trade.get('side')} {trade.get('symbol')}</b>\n"
                f"Amount: {trade.get('executedQty')} {trade.get('baseAsset')}\n"
                f"Price: {trade.get('avgPrice')}\n"
                f"Time: {trade.get('orderTime')}\n"
                f"Portfolio: {trade.get('portfolioLabel') or trade.get('portfolioId')}\n"
                f"-----------------------\n"
            )
            
        full_message = header + body
        self.send_message(full_message)

# Global singleton
telegram_bot = TelegramNotifier()

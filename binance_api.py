import json
import logging

import requests


class BinanceAPI:
    def __init__(self):
        self.url = "https://www.binance.com/bapi/futures/v1/friendly/future/copy-trade/lead-portfolio/order-history"
        self.base_headers = {
            "accept": "*/*",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "clienttype": "web",
            "content-type": "application/json",
            "lang": "en-IN",
            "origin": "https://www.binance.com",
            "referer": "https://www.binance.com/en-IN/copy-trading",
            "user-agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            ),
        }

    def fetch_orders(self, portfolio_id, start_time: int, end_time: int, page_size: int = 100):
        payload = {
            "portfolioId": str(portfolio_id),
            "startTime": start_time,
            "endTime": end_time,
            "pageSize": page_size,
        }

        try:
            response = requests.post(
                self.url,
                headers=self.base_headers,
                data=json.dumps(payload),
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            if data.get("success") and "data" in data and "list" in data["data"]:
                return data["data"]["list"]

            logging.error("Failed to fetch portfolio %s: %s", portfolio_id, data)
            return []
        except requests.exceptions.RequestException as exc:
            logging.error("Error fetching portfolio %s: %s", portfolio_id, exc)
            return []

import json
import logging
import os
from copy import deepcopy


class PortfolioConfigStore:
    def __init__(self, filename="portfolio_config.json"):
        self.filename = filename

    def _default_data(self):
        return {"portfolios": []}

    def load(self):
        if not os.path.exists(self.filename):
            return self._default_data()

        try:
            with open(self.filename, "r", encoding="utf-8") as file_handle:
                data = json.load(file_handle)
        except (OSError, json.JSONDecodeError) as exc:
            logging.error("Failed to load %s: %s", self.filename, exc)
            return self._default_data()

        if "portfolios" not in data or not isinstance(data["portfolios"], list):
            return self._default_data()
        return data

    def save(self, data):
        os.makedirs(os.path.dirname(self.filename) or ".", exist_ok=True)
        with open(self.filename, "w", encoding="utf-8") as file_handle:
            json.dump(data, file_handle, indent=2)

    def list_portfolios(self):
        data = self.load()
        portfolios = []
        for portfolio in data["portfolios"]:
            portfolio_id = str(portfolio.get("portfolio_id", "")).strip()
            if not portfolio_id:
                continue

            portfolios.append(
                {
                    "portfolio_id": portfolio_id,
                    "label": portfolio.get("label") or portfolio_id,
                    "enabled": bool(portfolio.get("enabled", True)),
                }
            )
        return portfolios

    def ensure_default(self, portfolio_id):
        if not self.list_portfolios():
            self.upsert_portfolio(portfolio_id=portfolio_id)

    def upsert_portfolio(self, portfolio_id, label=None, enabled=True):
        portfolio_id = str(portfolio_id).strip()
        data = self.load()
        portfolios = deepcopy(data["portfolios"])

        updated = False
        for portfolio in portfolios:
            if str(portfolio.get("portfolio_id")) == portfolio_id:
                if label is not None:
                    portfolio["label"] = label.strip() or portfolio_id
                portfolio["enabled"] = enabled
                updated = True
                break

        if not updated:
            portfolios.append(
                {
                    "portfolio_id": portfolio_id,
                    "label": label.strip() if label else portfolio_id,
                    "enabled": enabled,
                }
            )

        data["portfolios"] = portfolios
        self.save(data)
        return self.get_portfolio(portfolio_id)

    def remove_portfolio(self, portfolio_id):
        portfolio_id = str(portfolio_id).strip()
        data = self.load()
        original_count = len(data["portfolios"])
        data["portfolios"] = [
            portfolio for portfolio in data["portfolios"] if str(portfolio.get("portfolio_id")) != portfolio_id
        ]
        self.save(data)
        return len(data["portfolios"]) != original_count

    def get_portfolio(self, portfolio_id):
        portfolio_id = str(portfolio_id).strip()
        for portfolio in self.list_portfolios():
            if portfolio["portfolio_id"] == portfolio_id:
                return portfolio
        return None

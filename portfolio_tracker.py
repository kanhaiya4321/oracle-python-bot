import datetime
import logging

from excel_manager import ExcelManager


class PortfolioTracker:
    def __init__(self, portfolio_config, api, notifier, excel_filename):
        self.portfolio_config = portfolio_config
        self.api = api
        self.notifier = notifier
        self.excel_manager = ExcelManager(
            filename=excel_filename,
            portfolio_id=portfolio_config["portfolio_id"],
            portfolio_label=portfolio_config["label"],
        )

    @property
    def signature(self):
        return (
            self.portfolio_config["portfolio_id"],
            self.portfolio_config["label"],
            self.portfolio_config["enabled"],
        )

    def run_cycle(self):
        if not self.portfolio_config.get("enabled", True):
            return

        portfolio_id = self.portfolio_config["portfolio_id"]
        end_time_ms = int(datetime.datetime.now().timestamp() * 1000)
        start_time_ms = end_time_ms - 172800000

        logging.info("Fetching trades for portfolio %s", portfolio_id)
        trades = self.api.fetch_orders(
            portfolio_id=portfolio_id,
            start_time=start_time_ms,
            end_time=end_time_ms,
            page_size=100,
        )

        new_trades = self.excel_manager.process_new_trades(trades)
        if new_trades:
            self.notifier.format_and_send_trades(new_trades, self.portfolio_config)


class PortfolioTrackerManager:
    def __init__(self, api, notifier, excel_filename="binance_trades.xlsx"):
        self.api = api
        self.notifier = notifier
        self.excel_filename = excel_filename
        self.trackers = {}

    def sync(self, portfolio_configs):
        active_ids = set()

        for portfolio_config in portfolio_configs:
            portfolio_id = portfolio_config["portfolio_id"]
            active_ids.add(portfolio_id)
            existing_tracker = self.trackers.get(portfolio_id)

            if existing_tracker and existing_tracker.signature == (
                portfolio_config["portfolio_id"],
                portfolio_config["label"],
                portfolio_config["enabled"],
            ):
                continue

            self.trackers[portfolio_id] = PortfolioTracker(
                portfolio_config=portfolio_config,
                api=self.api,
                notifier=self.notifier,
                excel_filename=self.excel_filename,
            )
            logging.info("Tracker ready for portfolio %s", portfolio_id)

        removed_ids = set(self.trackers) - active_ids
        for portfolio_id in removed_ids:
            self.trackers.pop(portfolio_id, None)
            logging.info("Stopped tracking portfolio %s", portfolio_id)

    def run_cycle(self):
        for tracker in self.trackers.values():
            tracker.run_cycle()

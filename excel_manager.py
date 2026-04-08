import pandas as pd
import os
import logging

class ExcelManager:
    def __init__(self, filename="binance_trades.xlsx", portfolio_id=None, portfolio_label=None):
        self.filename = filename
        self.portfolio_id = str(portfolio_id) if portfolio_id else None
        self.portfolio_label = portfolio_label or self.portfolio_id
        self.columns = [
            "portfolioId",
            "portfolioLabel",
            "symbol", "orderTime", "baseAsset", "quoteAsset", "side", "type", 
            "positionSide", "executedQty", "avgPrice", "totalPnl", 
            "orderUpdateTime"
        ]
        
        # Initialize the file if it doesn't exist
        os.makedirs(os.path.dirname(self.filename) or ".", exist_ok=True)
        if not os.path.exists(self.filename):
            df = pd.DataFrame(columns=self.columns)
            df.to_excel(self.filename, index=False)
            logging.info(f"Created new Excel file: {self.filename}")

    def _prepare_existing_df(self):
        if not os.path.exists(self.filename):
            return pd.DataFrame(columns=self.columns)

        existing_df = pd.read_excel(self.filename)
        for col in self.columns:
            if col not in existing_df.columns:
                existing_df[col] = None
        existing_df = existing_df[self.columns]

        if not existing_df.empty and "orderTime" in existing_df.columns:
            existing_df["orderTime"] = pd.to_datetime(
                existing_df["orderTime"],
                format="%d-%m-%Y %H:%M:%S",
                errors="coerce",
            )
        return existing_df

    def _prepare_incoming_df(self, new_trades):
        incoming_df = pd.DataFrame(new_trades)
        if incoming_df.empty:
            return pd.DataFrame(columns=self.columns)

        incoming_df["portfolioId"] = self.portfolio_id
        incoming_df["portfolioLabel"] = self.portfolio_label

        if "orderTime" in incoming_df.columns:
            incoming_df["orderTime"] = pd.to_datetime(incoming_df["orderTime"], unit="ms", errors="coerce") \
                .dt.tz_localize("UTC") \
                .dt.tz_convert("Asia/Kolkata") \
                .dt.tz_localize(None) \
                .dt.floor("s")

        for col in self.columns:
            if col not in incoming_df.columns:
                incoming_df[col] = None
        return incoming_df[self.columns]

    def process_new_trades(self, new_trades):
        """
        Receives new trades, deduplicates against existing records,
        appends the new unique records, and sorts by orderTime ascending.
        """
        if not new_trades:
            return []

        try:
            existing_df = self._prepare_existing_df()
            incoming_df = self._prepare_incoming_df(new_trades)

            dedup_subset = ["orderTime", "symbol", "side", "executedQty"]
            incoming_df.drop_duplicates(subset=dedup_subset, keep="last", inplace=True)

            if existing_df.empty:
                new_records_only = incoming_df.copy()
            else:
                existing_keys = existing_df[dedup_subset].drop_duplicates()
                new_records_only = incoming_df.merge(
                    existing_keys,
                    on=dedup_subset,
                    how="left",
                    indicator=True,
                )
                new_records_only = new_records_only[new_records_only["_merge"] == "left_only"]
                new_records_only = new_records_only.drop(columns=["_merge"])

            if new_records_only.empty:
                logging.info("No new unique trades to add for %s.", self.portfolio_id)
                return []

            combined_df = pd.concat([existing_df, new_records_only], ignore_index=True)
            combined_df.drop_duplicates(subset=dedup_subset, keep="last", inplace=True)
            combined_df.sort_values(by="orderTime", ascending=True, inplace=True)

            save_df = combined_df.copy()
            save_df["orderTime"] = save_df["orderTime"].dt.strftime("%d-%m-%Y %H:%M:%S")
            save_df.to_excel(self.filename, index=False)

            new_records_only.sort_values(by="orderTime", ascending=True, inplace=True)
            logging.info("Added %s new unique trades to %s.", len(new_records_only), self.filename)
            result_df = new_records_only.copy()
            result_df["orderTime"] = result_df["orderTime"].dt.strftime("%d-%m-%Y %H:%M:%S")
            return result_df.to_dict("records")
        except Exception as e:
            logging.error(f"Error updating Excel file: {e}")
            return []

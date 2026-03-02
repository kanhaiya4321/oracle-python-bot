import pandas as pd
import os
import logging
from event_bus import bus

class ExcelManager:
    def __init__(self, filename="binance_trades.xlsx"):
        self.filename = filename
        self.columns = [
            "symbol", "orderTime", "baseAsset", "quoteAsset", "side", "type", 
            "positionSide", "executedQty", "avgPrice", "totalPnl", 
            "orderUpdateTime"
        ]
        
        # Initialize the file if it doesn't exist
        if not os.path.exists(self.filename):
            df = pd.DataFrame(columns=self.columns)
            df.to_excel(self.filename, index=False)
            logging.info(f"Created new Excel file: {self.filename}")

    def process_new_trades(self, new_trades):
        """
        Receives new trades, deduplicates against existing records,
        appends the new unique records, and sorts by orderTime ascending.
        """
        if not new_trades:
            return

        try:
            # Read existing data
            existing_df = pd.read_excel(self.filename)
            if not existing_df.empty and "orderTime" in existing_df.columns:
                existing_df["orderTime"] = pd.to_datetime(existing_df["orderTime"], format='%d-%m-%Y %H:%M:%S', errors='coerce')
            
            # Convert incoming trades to a DataFrame
            incoming_df = pd.DataFrame(new_trades)
            
            # Convert orderTime to IST
            if "orderTime" in incoming_df.columns:
                incoming_df["orderTime"] = pd.to_datetime(incoming_df["orderTime"], unit='ms') \
                    .dt.tz_localize('UTC') \
                    .dt.tz_convert('Asia/Kolkata') \
                    .dt.tz_localize(None) \
                    .dt.floor('s') # Remove milliseconds for string formatting match
            
            # Keep only the relevant columns
            for col in self.columns:
                if col not in incoming_df.columns:
                    incoming_df[col] = None
            incoming_df = incoming_df[self.columns]
            
            # A trade is considered unique based on a composite key:
            dedup_subset = ["orderTime", "symbol", "side", "executedQty"]
            
            # Ensure existing_df is empty or ensure its types match incoming_df
            if existing_df.empty:
                combined_df = incoming_df.copy()
            else:
                combined_df = pd.concat([existing_df, incoming_df], ignore_index=True)            
            
            # Deduplicate
            initial_count = len(combined_df)
            combined_df.drop_duplicates(subset=dedup_subset, keep="last", inplace=True)
            
            added_count = len(combined_df) - len(existing_df)
            
            if added_count > 0:
                # Sort the dataframe by orderTime ascending (oldest first, latest record at the end)
                combined_df.sort_values(by="orderTime", ascending=True, inplace=True)
                
                # Format orderTime to string before saving
                save_df = combined_df.copy()
                save_df["orderTime"] = save_df["orderTime"].dt.strftime('%d-%m-%Y %H:%M:%S')
                
                # Write back to Excel
                save_df.to_excel(self.filename, index=False)
                logging.info(f"Added {added_count} new unique trades to {self.filename}.")
                
                # Publish event for newly added trades
                new_records_only = combined_df.tail(added_count).to_dict('records')
                bus.publish("on_new_trades_saved", new_records_only)
                
            else:
                logging.info("No new unique trades to add.")
                
        except Exception as e:
            logging.error(f"Error updating Excel file: {e}")

# data.py — Data Layer
# Handles all data fetching, caching, validation, and cleaning via yfinance

import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from typing import Optional


# Handles fetching, caching, and cleaning of stock data from Yahoo Finance
class StockDataService:

    # Fetches and cleans historical OHLCV data from Yahoo Finance for one or more tickers
    @staticmethod
    @st.cache_data
    def get_stock_data(tickers: list, start_date_str: str, end_date_str: str) -> Optional[pd.DataFrame]:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date   = datetime.strptime(end_date_str,   '%Y-%m-%d')

            now = datetime.now()
            if now.hour >= 16 and now.minute >= 30:
                end_date = max(end_date, now)

            end_date = end_date + timedelta(days=1)

            # 5-day buffer ensures data availability around weekends and bank holidays
            buffer_start = start_date - timedelta(days=5)

            raw_data = yf.download(
                tickers,
                start=buffer_start.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                progress=False,
                auto_adjust=False
            )

            if raw_data.empty:
                return None

            df = raw_data.copy()
            df = df.reset_index()
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df = df[df['Date'].notna()]
            df.set_index('Date', inplace=True)

            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            df.ffill(inplace=True)
            df.bfill(inplace=True)

            return df

        except Exception as e:
            st.error(f"Error fetching data: {e}")
            return None

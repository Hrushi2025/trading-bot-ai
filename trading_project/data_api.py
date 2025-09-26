# trading_project/data_api.py
import streamlit as st
import pandas as pd
import yfinance as yf # Example dependency

def fetch_historical_data(symbol: str, period: str = "1y") -> pd.DataFrame:
    """
    Fetches historical stock data using yfinance.

    Args:
        symbol (str): The stock ticker symbol (e.g., "AAPL").
        period (str): The period for which to fetch data (e.g., "1d", "5d", "1mo", "1y", "max").

    Returns:
        pd.DataFrame: DataFrame containing historical OHLCV data.
                      Returns an empty DataFrame if fetching fails.
    """
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        if data.empty:
            st.warning(f"No historical data found for symbol: {symbol}")
            return pd.DataFrame()
        return data
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()

def fetch_realtime_price(symbol: str) -> float:
    """
    Fetches the latest real-time price for a given symbol.
    Note: yfinance may not provide true real-time, but the latest available price.
    For true real-time, you'd typically need a dedicated API.
    """
    try:
        ticker = yf.Ticker(symbol)
        # Get the last available row and extract the Close price
        latest_data = ticker.history(period="1d") # Fetching just one day to get latest
        if not latest_data.empty:
            return latest_data['Close'].iloc[-1]
        else:
            st.warning(f"Could not fetch latest price for {symbol}.")
            return None
    except Exception as e:
        st.error(f"Error fetching real-time price for {symbol}: {e}")
        return None

# Add other data fetching functions here, e.g., for specific APIs if needed
# def fetch_from_alpha_vantage(symbol: str) -> pd.DataFrame:
#     api_key = st.secrets["api"]["alpha_vantage_key"]
#     # ... implementation using alpha_vantage library ...

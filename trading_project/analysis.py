# trading_project/analysis.py
import pandas as pd

def calculate_sma(data: pd.DataFrame, window: int = 20) -> pd.Series:
    """Calculates the Simple Moving Average (SMA)."""
    if 'Close' not in data.columns:
        return pd.Series(dtype=float)
    return data['Close'].rolling(window=window).mean()

def calculate_rsi(data: pd.DataFrame, window: int = 14) -> pd.Series:
    """Calculates the Relative Strength Index (RSI)."""
    if 'Close' not in data.columns:
        return pd.Series(dtype=float)

    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.ewm(com=window-1, adjust=False).mean() # Using EWMA for smoother average
    avg_loss = loss.ewm(com=window-1, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    # Handle division by zero where avg_loss is 0 (RSI should be 100)
    rsi = rsi.fillna(100)
    # RSI is undefined for the first 'window' periods, so set to NaN
    rsi.iloc[:window] = pd.NA

    return rsi

# Add other indicator functions here (e.g., MACD, Bollinger Bands)

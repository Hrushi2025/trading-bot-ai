# trading_project/strategies.py
import pandas as pd
from trading_project.analysis import calculate_sma, calculate_rsi

def generate_signals(data: pd.DataFrame, sma_window: int = 20, rsi_window: int = 14, rsi_oversold: int = 30, rsi_overbought: int = 70) -> pd.DataFrame:
    """
    Generates buy/sell signals based on SMA crossover and RSI levels.

    Args:
        data (pd.DataFrame): DataFrame with 'Close', 'SMA', 'RSI' columns.
        sma_window (int): Window size for SMA.
        rsi_window (int): Window size for RSI.
        rsi_oversold (int): RSI threshold for buy signal.
        rsi_overbought (int): RSI threshold for sell signal.

    Returns:
        pd.DataFrame: Original DataFrame with added 'Signal' column (1: Buy, -1: Sell, 0: Hold).
    """
    if data.empty:
        return pd.DataFrame()

    # Calculate indicators if they don't exist (though ideally they are pre-calculated)
    if 'SMA' not in data.columns:
        data['SMA'] = calculate_sma(data, window=sma_window)
    if 'RSI' not in data.columns:
        data['RSI'] = calculate_rsi(data, window=rsi_window)

    # Initialize signal column
    data['Signal'] = 0

    # Ensure indicator columns are not all NaN for logic to work
    if data['SMA'].isnull().all() or data['RSI'].isnull().all():
        print("Warning: Indicator calculation resulted in all NaNs. Check data or window sizes.")
        return data # Cannot generate signals without valid indicators

    # Define Buy Condition: Price crosses above SMA AND RSI is oversold
    buy_condition = (data['Close'] > data['SMA']) & (data['RSI'] < rsi_oversold) & (data['SMA'].notna()) & (data['RSI'].notna())

    # Define Sell Condition: Price crosses below SMA AND RSI is overbought
    sell_condition = (data['Close'] < data['SMA']) & (data['RSI'] > rsi_overbought) & (data['SMA'].notna()) & (data['RSI'].notna())

    # Apply signals
    data.loc[buy_condition, 'Signal'] = 1
    data.loc[sell_condition, 'Signal'] = -1

    # Optional: Remove consecutive signals for a cleaner strategy
    # For simplicity, we'll leave it as is for now.

    return data

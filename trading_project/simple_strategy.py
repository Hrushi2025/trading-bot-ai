# auto_trading_project/strategy.py

def simple_strategy(current_price: float, moving_avg: float, thresholds: dict) -> str:
    """
    A simple moving average based strategy.

    Args:
        current_price: The current trading price.
        moving_avg: The calculated moving average.
        thresholds: Dictionary containing 'buy' and 'sell' thresholds.
                      Example: {"buy": 0.02, "sell": 0.03}

    Returns:
        "BUY", "SELL", or "HOLD"
    """
    buy_threshold = thresholds.get("buy", 0.02) # Default if not provided
    sell_threshold = thresholds.get("sell", 0.03) # Default if not provided

    if current_price < moving_avg * (1 - buy_threshold):
        return "BUY"
    elif current_price > moving_avg * (1 + sell_threshold):
        return "SELL"
    else:
        return "HOLD"

# You can add more strategy functions here in the future, e.g.:
# def rsi_strategy(current_price, rsi_value, thresholds): ...
# def bollinger_bands_strategy(current_price, upper_band, lower_band, thresholds): ...

# auto_trading_project/simulator.py
import pandas as pd
import yaml
import os
import io  # For handling file-like objects

# --- Configuration ---
DEFAULT_INITIAL_BALANCE = 10000.0
DEFAULT_WINDOW_SIZE = 5  # For moving average calculation


# --- Helper Functions ---

def load_strategy_config_for_sim(file_path: str, strategy_name: str, passed_thresholds: dict = None) -> dict:
    """
    Loads strategy thresholds, prioritizing passed thresholds over config file.
    If passed_thresholds are provided, they are used directly.
    Otherwise, it attempts to load from the YAML config file.
    Falls back to default if neither is available.
    """
    if passed_thresholds and isinstance(passed_thresholds, dict):
        # Ensure passed_thresholds are in the expected format {param_name: value}
        return passed_thresholds

    # If no thresholds were passed, try loading from config file
    default_strategy_defaults = {
        "simple": {"buy": 0.02, "sell": 0.03, "window_size": DEFAULT_WINDOW_SIZE}
    }

    if not os.path.exists(file_path):
        print(f"Warning: Strategy config file not found at '{file_path}'. Using defaults.")
        return default_strategy_defaults.get(strategy_name, {})

    try:
        with open(file_path, 'r') as f:
            config = yaml.safe_load(f)

        # Get thresholds for the specific strategy, or fall back to general defaults
        strategy_specific_config = config.get(strategy_name, {})

        # Combine with default parameters if they are missing in the config file
        combined_config = default_strategy_defaults.get(strategy_name, {}).copy()
        combined_config.update(strategy_specific_config)

        return combined_config

    except Exception as e:
        print(f"Error loading strategy config for simulator: {e}")
        return default_strategy_defaults.get(strategy_name, {})


def run_simulation(data_source, strategy_name="simple", strategy_params=None, initial_balance=DEFAULT_INITIAL_BALANCE):
    """
    Runs the simulation engine.

    Args:
        data_source: Path to CSV file or a file-like object (StringIO).
        strategy_name: Name of the strategy to use (e.g., "simple").
        strategy_params: A dictionary of parameters for the selected strategy.
                         Example: {"buy": 0.02, "sell": 0.03, "window_size": 5}
                         These are prioritized over the config file.
        initial_balance: Starting balance for the simulation.

    Returns:
        A pandas DataFrame containing simulation results, or None if an error occurs.
    """
    print(f"Starting simulation with strategy: '{strategy_name}'")

    # --- Data Loading ---
    try:
        if isinstance(data_source, str):  # It's a file path
            df_prices = pd.read_csv(data_source)
            print(f"Loading data from file path: {data_source}")
        elif hasattr(data_source, 'read'):  # It's a file-like object (e.g., StringIO)
            df_prices = pd.read_csv(data_source)
            print("Loading data from file-like object.")
        else:
            raise ValueError("Invalid data_source provided. Must be a file path or file-like object.")

        # Ensure required columns exist and are in correct format
        required_cols = ['timestamp', 'price']
        if not all(col in df_prices.columns for col in required_cols):
            missing = [col for col in required_cols if col not in df_prices.columns]
            raise ValueError(f"CSV must contain '{required_cols}'. Missing: {missing}")

        df_prices['timestamp'] = pd.to_datetime(df_prices['timestamp'])
        df_prices.set_index('timestamp', inplace=True)
        df_prices.sort_index(inplace=True)  # Ensure chronological order

    except FileNotFoundError:
        print(f"Error: Data file not found at {data_source}")
        return None
    except ValueError as ve:
        print(f"Data Error: {ve}")
        return None
    except Exception as e:
        print(f"Error loading or processing data: {e}")
        import traceback
        traceback.print_exc()
        return None

    # --- Strategy Configuration Loading ---
    # Prioritize strategy_params passed directly from the app
    # Fallback to loading from strategy_config.yaml
    strategy_config_path = 'auto_trading_project/strategy_config.yaml'  # Adjust path if needed
    current_strategy_thresholds = load_strategy_config_for_sim(
        file_path=strategy_config_path,
        strategy_name=strategy_name,
        passed_thresholds=strategy_params  # This is the key: prioritize passed params
    )

    if not current_strategy_thresholds:
        print(f"Error: Could not determine strategy parameters for '{strategy_name}'.")
        return None

    print(f"Using strategy parameters for '{strategy_name}': {current_strategy_thresholds}")

    # --- Simulation Core Logic ---
    balance = initial_balance
    position = 0  # Number of shares held
    simulation_logs = []

    # --- Strategy-Specific Calculations ---
    # Example: Moving Average calculation for 'simple' strategy
    window_size = current_strategy_thresholds.get("window_size", DEFAULT_WINDOW_SIZE)
    if 'price' in df_prices.columns:
        df_prices['moving_avg'] = df_prices['price'].rolling(window=window_size).mean()
    else:
        print("Warning: 'price' column not found, cannot calculate moving average.")
        return None  # Cannot proceed without price

    # --- Iteration through Data ---
    for index, row in df_prices.iterrows():
        current_price = row['price']
        moving_avg = row.get('moving_avg')  # Use .get() in case 'moving_avg' column wasn't created or has NaN

        action = "HOLD"
        reason = "Initialization"
        buy_quantity = 0
        sell_quantity = 0

        # Check if moving_avg is valid for strategies that need it
        if pd.isna(moving_avg) and strategy_name == "simple":
            reason = f"Insufficient data for moving average (window={window_size})"
        else:
            # --- Strategy Execution ---
            # This part needs to dynamically call the correct strategy function.
            # For now, we'll hardcode it for 'simple'. In a more advanced system,
            # you'd map strategy names to functions.
            if strategy_name == "simple":
                # Ensure the strategy function can handle potential missing params if not all are provided
                action = simple_strategy(
                    current_price=current_price,
                    moving_avg=moving_avg,
                    thresholds={
                        "buy": current_strategy_thresholds.get("buy"),
                        "sell": current_strategy_thresholds.get("sell")
                    }
                )
            # elif strategy_name == "rsi_strategy":
            #     rsi_value = row.get('rsi') # Assuming RSI is calculated and available
            #     action = rsi_strategy(current_price, rsi_value, current_strategy_thresholds)
            else:
                reason = f"Strategy '{strategy_name}' not implemented in simulator."
                action = "HOLD"

        # --- Decision Logic & Trade Execution Simulation ---
        if action == "BUY":
            # Simplified: Buy 1 share if we have enough balance and no position
            # In a real system, quantity would be dynamic
            quantity_to_buy_sell = 1  # Default fixed quantity
            cost = current_price * quantity_to_buy_buy

            if balance >= cost and position == 0:  # Check balance and no existing position
                balance -= cost
                position += quantity_to_buy_sell
                reason = f"BUY Executed: Price={current_price:.2f}, MA={moving_avg:.2f}"
            else:
                action = "HOLD"  # Override to HOLD if conditions not met
                reason = f"BUY Recommended, but HOLD: Price={current_price:.2f}, MA={moving_avg:.2f} (Balance={balance:.2f}, Pos={position})"

        elif action == "SELL":
            # Simplified: Sell 1 share if we have a position
            quantity_to_buy_sell = 1  # Default fixed quantity
            revenue = current_price * quantity_to_buy_sell

            if position >= quantity_to_buy_sell:  # Check if we have enough to sell
                balance += revenue
                position -= quantity_to_buy_sell
                reason = f"SELL Executed: Price={current_price:.2f}, MA={moving_avg:.2f}"
            else:
                action = "HOLD"  # Override to HOLD if conditions not met
                reason = f"SELL Recommended, but HOLD: Price={current_price:.2f}, MA={moving_avg:.2f} (Pos={position})"

        # Ensure if action was HOLD, quantity is 0
        if action == "HOLD":
            buy_quantity = 0
            sell_quantity = 0
            # If reason wasn't set by buy/sell recommendation failure, set a generic HOLD reason
            if "Recommended" not in reason and "Executed" not in reason and "Insufficient" not in reason and "not implemented" not in reason:
                reason = f"HOLD: Price={current_price:.2f}, MA={moving_avg:.2f}"

        # --- Update Portfolio Value & Log ---
        portfolio_value = balance + (position * current_price)

        # Log details for this step
        simulation_logs.append({
            'timestamp': index,  # This is a datetime object, will format later
            'user_id': 'demo_user',  # Placeholder, could be an input
            'symbol': 'AAPL',  # Placeholder, could be an input
            'side': action,
            'quantity': quantity_to_buy_sell if action in ["BUY", "SELL"] else 0,
            'strategy': strategy_name,
            'reason': reason,
            'balance': balance,
            'position': position,
            'portfolio_value': portfolio_value
        })

        # Reset quantities for next iteration if they were used
        quantity_to_buy_sell = 0

    if not simulation_logs:
        print("No simulation logs were generated.")
        return None

    # Convert logs to DataFrame
    results_df = pd.DataFrame(simulation_logs)

    # Format timestamp for consistency with your example output
    results_df['timestamp'] = results_df['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    print(f"Simulation finished. Total logs: {len(results_df)}")
    return results_df

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

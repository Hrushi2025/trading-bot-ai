# simulator.py (Modified for Streamlit app)
import pandas as pd
import yaml
import os

# Assuming your strategy.py and its functions are accessible
from strategy import simple_strategy  # Or whatever strategies you have

# Define default thresholds if config file is missing
DEFAULT_THRESHOLDS = {"simple": {"buy": 0.02, "sell": 0.03}}
DEFAULT_INITIAL_BALANCE = 10000  # Or get this from somewhere


def load_config_for_simulator(file_path, strategy_name, passed_thresholds):
    """Loads strategy thresholds, prioritizing passed thresholds over config file."""
    if passed_thresholds:
        # Use thresholds passed directly from the app (e.g., via selectbox/number_input)
        return passed_thresholds

    # Fallback to config file if no thresholds were passed (less likely with Streamlit's input widgets)
    if not os.path.exists(file_path):
        print(f"Warning: Strategy config file not found at '{file_path}'. Using default thresholds.")
        return DEFAULT_THRESHOLDS.get(strategy_name, {})

    try:
        with open(file_path, 'r') as f:
            config = yaml.safe_load(f)
        return config.get(strategy_name, {})
    except Exception as e:
        print(f"Error loading strategy config for simulator: {e}")
        return DEFAULT_THRESHOLDS.get(strategy_name, {})


def run_simulation(data_source, strategy_name="simple", thresholds=None, initial_balance=10000):
    """
    Runs the simulation engine.

    Args:
        data_source: Path to CSV file or a file-like object (StringIO).
        strategy_name: Name of the strategy to use (e.g., "simple").
        thresholds: A dictionary of thresholds for the selected strategy.
                    Example: {"buy": 0.02, "sell": 0.03}
        initial_balance: Starting balance for the simulation.

    Returns:
        A pandas DataFrame containing simulation results, or None if an error occurs.
    """
    try:
        if isinstance(data_source, str):  # It's a file path
            df_prices = pd.read_csv(data_source)
        elif hasattr(data_source, 'read'):  # It's a file-like object (e.g., StringIO)
            df_prices = pd.read_csv(data_source)
        else:
            raise ValueError("Invalid data_source provided. Must be a file path or file-like object.")

        # Ensure required columns exist
        if 'timestamp' not in df_prices.columns or 'price' not in df_prices.columns:
            raise ValueError("CSV must contain 'timestamp' and 'price' columns.")

        # Preprocess timestamp if it's not already datetime
        df_prices['timestamp'] = pd.to_datetime(df_prices['timestamp'])
        df_prices.set_index('timestamp', inplace=True)
        df_prices.sort_index(inplace=True)  # Ensure chronological order

        # --- Strategy Configuration Loading ---
        # This part needs careful integration. The 'thresholds' parameter directly from Streamlit is preferred.
        # If 'thresholds' is None, then we might fall back to loading from a config file.
        # Let's assume 'thresholds' passed from Streamlit IS the definitive config.

        if thresholds is None:
            # Fallback if Streamlit didn't pass any (shouldn't happen with the app.py code above)
            strategy_config_path = 'auto_trading_project/strategy_config.yaml'  # Adjust path if needed
            current_strategy_thresholds = load_config_for_simulator(strategy_config_path, strategy_name, None)
            print(f"Warning: No explicit thresholds passed to simulator. Falling back to config/defaults.")
        else:
            # Use thresholds passed directly from the Streamlit app
            current_strategy_thresholds = thresholds
            print(f"Using thresholds passed from Streamlit: {current_strategy_thresholds}")

        if not current_strategy_thresholds:  # If even fallback yields nothing
            print(f"Error: Could not determine thresholds for strategy '{strategy_name}'.")
            return None

        # --- Simulation Core Logic ---
        balance = initial_balance
        position = 0  # Number of shares held
        portfolio_value = initial_balance
        simulation_logs = []

        # Calculate Moving Average (example)
        window_size = 5  # Example window size for moving average
        df_prices['moving_avg'] = df_prices['price'].rolling(window=window_size).mean()

        for index, row in df_prices.iterrows():
            current_price = row['price']
            moving_avg = row['moving_avg']

            # Ensure moving_avg is not NaN (happens at the beginning of rolling calculation)
            if pd.isna(moving_avg):
                action = "HOLD"
                reason = "Insufficient data for moving average"
            else:
                # Call your specific strategy function
                # This needs to match the signature expected by the strategy function
                if strategy_name == "simple":
                    action = simple_strategy(
                        current_price=current_price,
                        moving_avg=moving_avg,
                        thresholds=current_strategy_thresholds  # Pass the loaded/selected thresholds
                    )
                else:
                    action = "HOLD"  # Default for unknown strategies
                    reason = f"Strategy '{strategy_name}' not implemented"

                # --- Decision Logic based on Action ---
                if action == "BUY":
                    # Simplified: Buy 1 share if we have enough balance and no position
                    # In a real system, quantity would be dynamic (e.g., based on balance, risk, fixed amount)
                    buy_quantity = 1  # Fixed quantity for simplicity
                    if balance >= current_price * buy_quantity and position == 0:
                        balance -= current_price * buy_quantity
                        position += buy_quantity
                        reason = f"Price={current_price:.2f}, MA={moving_avg:.2f}. BUY executed."
                    else:
                        action = "HOLD"
                        reason = f"Price={current_price:.2f}, MA={moving_avg:.2f}. BUY recommended, but cannot execute (balance={balance:.2f}, position={position})."
                elif action == "SELL":
                    # Simplified: Sell 1 share if we have a position
                    sell_quantity = 1  # Fixed quantity for simplicity
                    if position >= sell_quantity:
                        balance += current_price * sell_quantity
                        position -= sell_quantity
                        reason = f"Price={current_price:.2f}, MA={moving_avg:.2f}. SELL executed."
                    else:
                        action = "HOLD"
                        reason = f"Price={current_price:.2f}, MA={moving_avg:.2f}. SELL recommended, but cannot execute (no position to sell)."
                else:  # HOLD
                    reason = f"Price={current_price:.2f}, MA={moving_avg:.2f}. Holding."

            # Update portfolio value for logging
            portfolio_value = balance + (position * current_price)

            # Log the action
            simulation_logs.append({
                'timestamp': index,  # This is a datetime object
                'user_id': 'demo_user',  # Or get from input/config
                'symbol': 'AAPL',  # Or get from input/config
                'side': action,
                'quantity': buy_quantity if action == "BUY" else (sell_quantity if action == "SELL" else 0),
                'strategy': strategy_name,
                'reason': reason,
                'balance': balance,
                'position': position,
                'portfolio_value': portfolio_value
            })

            # Reset buy/sell quantities for next iteration
            buy_quantity = 0
            sell_quantity = 0

        if not simulation_logs:
            return None  # No simulation ran

        # Convert logs to DataFrame
        results_df = pd.DataFrame(simulation_logs)
        results_df['timestamp'] = results_df['timestamp'].dt.strftime(
            '%Y-%m-%dT%H:%M:%SZ')  # Format timestamp for consistency with example

        # Optional: Save to CSV here if the app.py doesn't handle it externally
        # results_df.to_csv('simulation_output.csv', index=False)

        return results_df

    except FileNotFoundError:
        print(f"Error: Data file not found at {data_source}")
        return None
    except ValueError as ve:
        print(f"Data Error: {ve}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred in simulator: {e}")
        import traceback
        traceback.print_exc()
        return None


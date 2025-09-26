# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

# --- Import functions from your modules ---
from trading_project.data_api import fetch_historical_data, fetch_realtime_price
from trading_project.analysis import calculate_sma, calculate_rsi
from trading_project.strategies import generate_signals
from trading_project.utils import format_date_for_display

# --- Streamlit App Configuration ---
st.set_page_config(page_title="Trading Bot Dashboard", layout="wide")
st.title("Trading Bot Dashboard")

# --- Sidebar for User Inputs ---
with st.sidebar:
    st.header("Settings")
    symbol = st.text_input("Stock Symbol", "AAPL").upper()
    data_period = st.selectbox("Data Period", ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"], index=5) # Default to 1 year

    st.subheader("Strategy Parameters")
    sma_window = st.slider("SMA Window", 5, 50, 20)
    rsi_window = st.slider("RSI Window", 5, 30, 14)
    rsi_oversold = st.slider("RSI Oversold Threshold", 0, 50, 30)
    rsi_overbought = st.slider("RSI Overbought Threshold", 50, 100, 70)

    # Example of using secrets (if you had an API key for another source)
    # api_key = st.secrets.get("api", {}).get("your_api_key_name")
    # if not api_key:
    #     st.warning("API key not found. Some features may not work.")

    run_analysis = st.button("Run Analysis")

# --- Main App Logic ---
if run_analysis and symbol:
    st.header(f"Analysis for {symbol}")

    # Fetch Data
    data = fetch_historical_data(symbol, period=data_period)

    if not data.empty:
        # Ensure index is datetime for plotting
        data.index = pd.to_datetime(data.index)

        # Calculate Indicators
        data['SMA'] = calculate_sma(data, window=sma_window)
        data['RSI'] = calculate_rsi(data, window=rsi_window)

        # Generate Signals
        data_with_signals = generate_signals(
            data.copy(), # Pass a copy to avoid modifying original data if used elsewhere
            sma_window=sma_window,
            rsi_window=rsi_window,
            rsi_oversold=rsi_oversold,
            rsi_overbought=rsi_overbought
        )

        # --- Display Key Metrics ---
        col1, col2, col3 = st.columns(3)
        latest_close = data_with_signals['Close'].iloc[-1] if not data_with_signals.empty else "N/A"
        latest_sma = data_with_signals['SMA'].iloc[-1] if not data_with_signals.empty else "N/A"
        latest_rsi = data_with_signals['RSI'].iloc[-1] if not data_with_signals.empty else "N/A"

        col1.metric("Latest Close", f"${latest_close:.2f}" if isinstance(latest_close, (int, float)) else latest_close)
        col2.metric(f"SMA({sma_window})", f"${latest_sma:.2f}" if isinstance(latest_sma, (int, float)) else latest_sma)
        col3.metric(f"RSI({rsi_window})", f"{latest_rsi:.2f}" if isinstance(latest_rsi, (int, float)) else latest_rsi)

        # --- Plotting ---
        st.subheader("Price Action and Indicators")

        # Plot Price, SMA, and Signals
        fig_price = px.line(data_with_signals, x=data_with_signals.index, y='Close', title=f'{symbol} Price & SMA')
        fig_price.add_scatter(x=data_with_signals.index, y=data_with_signals['SMA'], mode='lines', name=f'SMA({sma_window})')

        # Add buy/sell markers
        buy_signals = data_with_signals[data_with_signals['Signal'] == 1]
        sell_signals = data_with_signals[data_with_signals['Signal'] == -1]

        fig_price.add_scatter(x=buy_signals.index, y=buy_signals['Close'], mode='markers', marker_symbol='triangle-up', marker_color='green', marker_size=10, name='Buy Signal')
        fig_price.add_scatter(x=sell_signals.index, y=sell_signals['Close'], mode='markers', marker_symbol='triangle-down', marker_color='red', marker_size=10, name='Sell Signal')

        st.plotly_chart(fig_price, use_container_width=True)

        # Plot RSI
        st.subheader("Relative Strength Index (RSI)")
        fig_rsi = px.line(data_with_signals, x=data_with_signals.index, y='RSI', title=f'{symbol} RSI ({rsi_window})')
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought", annotation_position="bottom right")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold", annotation_position="bottom right")
        st.plotly_chart(fig_rsi, use_container_width=True)

        # --- Display Data Table ---
        st.subheader("Historical Data with Signals")
        st.dataframe(data_with_signals.tail()) # Show last few rows

    else:
        st.warning("No data fetched. Please check the symbol and network connection.")

elif symbol:
    st.info("Click 'Run Analysis' to see the results.")
else:
    st.warning("Please enter a stock symbol in the sidebar.")


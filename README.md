##Auto-Trading Recommendation System
---
This project implements a smart auto-trading recommendation system with:

Configurable strategy engine for buy/sell signals

AI-driven prediction and user-defined threshold based suggestions

Automated trade execution for premium users

Logging of AI-generated trade actions for transparency

Trade simulation sandbox for backtesting and testing strategies

Web dashboard using Streamlit for interactive usage and visualization
---
Features
1. Recommendation Engine
Uses technical analysis indicators like SMA (Simple Moving Average) and RSI (Relative Strength Index)

Generates buy/sell signals based on strategy parameters and AI predictions

User-configurable thresholds for overbought/oversold conditions and window sizes
---
2. Automated Trading
For premium users, executes trades automatically based on recommendations

Supports API endpoints for trade execution and integration

Maintains logs of all AI-generated signals and trade decisions separately
---
3. Trade Simulation Sandbox
Allows users to test strategies and simulate trades without risking actual capital

Visualizes historical performance and key metrics to evaluate strategies
---
4. Streamlit Web Dashboard
Interactive UI for users to select stock symbols, data periods, and strategy parameters

Displays plots, trade signals, and key analytics in real-time

Easy-to-use sidebar controls for configuration
---
Project Structure
text

<img width="2048" height="2048" alt="image" src="https://github.com/user-attachments/assets/ab444152-f3d8-4e5c-8a80-1e415fbb38ea" />

Prerequisites
Python 3.8 or higher
---
Virtual environment setup recommended

Installed packages in requirements.txt, including:

streamlit

pandas

plotly
---
other dependencies as used in the code

Setup and Installation
Clone the repository:

bash
git clone https://github.com/Hrushi2025/trading-bot-ai.git
cd trading-bot-ai
Create and activate a virtual environment:

bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
Install dependencies:

bash
pip install -r requirements.txt
Run the Streamlit app:

bash
cd trading_project
streamlit run app.py
---
Usage
Use the sidebar to select stock symbols and data period.

Adjust strategy parameters like SMA window size, RSI thresholds.

Click "Run Analysis" to generate and view trade recommendations.

Premium users can enable Auto-Trade to execute trades automatically.

Use the simulation sandbox to backtest strategies before deploying.
---
Deployment
This app can be deployed on Streamlit Cloud or any cloud VM with Python support.

Streamlit Cloud
Push your code to GitHub.

Connect the repository on Streamlit Cloud.

Set up required secrets or environment variables if any.

Deploy and access your app instantly at the provided URL.
---
Manual VM Deployment
Ensure Python, pip, and venv are installed.

Clone the repo and set up virtual environment & dependencies.

Run the app with streamlit run app.py.

Use a reverse proxy or tunneling tool (e.g., ngrok) to make the app accessible externally.
---
Logging and Transparency
All AI-generated buy/sell signals and automated trade executions are logged separately.

Logs are maintained for auditing and transparency.
---
Contributing
Contributions are welcome! Please open issues or pull requests on GitHub.


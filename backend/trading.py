from flask import Flask, jsonify, request
import pandas as pd
import os
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Define the directory where CSV files are stored
directory = r"C:\Users\91790\Desktop\Interactive\backend\Financial Data"

# List of stock symbols
stock_symbols = [
    "AAPL", "MSFT", "GOOG", "AMZN", "TSLA", "SPY", "NVDA", "META", "NFLX", "AMD",
]

# Helper function to load and process data
def load_stock_data(filepath):
    try:
        stock_data = pd.read_csv(filepath, skiprows=2, names=['Date', 'Adj_Close', 'Close', 'High', 'Low', 'Open', 'Volume'])
        stock_data = stock_data[~stock_data['Date'].str.contains('Date', na=False)]
        stock_data['Date'] = pd.to_datetime(stock_data['Date'].str.split('.').str[0], format='%Y-%m-%d %H:%M:%S')
        stock_data.set_index('Date', inplace=True)
        return stock_data
    except Exception as e:
        raise ValueError(f"Error loading data: {str(e)}")

@app.route('/api/stocks/<ticker>/volume', methods=['GET'])
def get_trading_volume(ticker):
    """
    Return the stock trading volume data for a given stock ticker in JSON format for Plotly.
    """
    filepath = os.path.join(directory, f"{ticker}.csv")
    if not os.path.exists(filepath):
        return jsonify({"error": f"Data for {ticker} not found."}), 404

    try:
        stock_data = load_stock_data(filepath)

        # Prepare data for Plotly (Date and Volume)
        volume_data = {
            "x": stock_data.index.strftime('%Y-%m-%d').tolist(),  # Date as string list for Plotly
            "y": stock_data['Volume'].tolist(),  # Volume values as list
        }

        # Return the data as JSON
        return jsonify(volume_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5003)

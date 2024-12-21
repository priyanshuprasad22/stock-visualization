from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import os

app = Flask(__name__)
CORS(app)

# Load data into a global dictionary (simulate loaded stock data)
stock_symbols = ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA", "SPY", "NVDA", "META", "NFLX", "AMD"]
directory = r"C:\Users\91790\Desktop\Interactive\backend\Financial Data"
data = {}

# Load CSV data at startup
for symbol in stock_symbols:
    filepath = os.path.join(directory, f"{symbol}.csv")
    try:
        stock_data = pd.read_csv(filepath, skiprows=2, names=['Date', 'Adj_Close', 'Close', 'High', 'Low', 'Open', 'Volume'])
        stock_data = stock_data[~stock_data['Date'].str.contains('Date', na=False)]
        stock_data['Date'] = pd.to_datetime(stock_data['Date'].str.split('.').str[0], format='%Y-%m-%d %H:%M:%S')
        stock_data.set_index('Date', inplace=True)
        stock_data['Adj_Close'] = pd.to_numeric(stock_data['Adj_Close'], errors='coerce')
        data[symbol] = stock_data
    except Exception as e:
        print(f"Failed to load {symbol}: {e}")

# Utility Functions
def calculate_daily_returns(adj_close):
    return adj_close.pct_change().dropna()

@app.route('/stock/graph', methods=['GET'])
def stock_graph():
    symbols = request.args.get('symbols', '').split(',')
    graph_type = request.args.get('graph_type', 'daily_returns')

    if not symbols or not graph_type:
        return jsonify({"error": "Please provide 'symbols' and 'graph_type' parameters."}), 400

    # Validate symbols
    valid_symbols = [symbol for symbol in symbols if symbol in data]
    if not valid_symbols:
        return jsonify({"error": "No valid stock symbols provided."}), 400

    adj_close = pd.DataFrame({symbol: data[symbol]['Adj_Close'] for symbol in valid_symbols})

    fig = None  # Placeholder for the Plotly figure

    if graph_type == 'daily_returns':
        returns = adj_close.pct_change().dropna()
        fig = px.line(returns, labels={'value': 'Daily Return', 'index': 'Date'}, title='Daily Returns for Selected Symbols')

    elif graph_type == 'rolling_mean':
        sma = adj_close.rolling(window=20).mean()
        fig = px.line(sma, labels={'value': 'Rolling Mean', 'index': 'Date'}, title='Rolling Mean (20-day) for Selected Symbols')

    elif graph_type == 'bollinger_bands':
        fig = go.Figure()
        for symbol in valid_symbols:
            series = adj_close[symbol]
            sma = series.rolling(window=20).mean()
            std = series.rolling(window=20).std()
            upper_band = sma + (2 * std)
            lower_band = sma - (2 * std)

            fig.add_trace(go.Scatter(x=series.index, y=series, mode='lines', name=f'{symbol} Price'))
            fig.add_trace(go.Scatter(x=sma.index, y=sma, mode='lines', name=f'{symbol} SMA'))
            fig.add_trace(go.Scatter(x=upper_band.index, y=upper_band, mode='lines', fill=None, name=f'{symbol} Upper Band'))
            fig.add_trace(go.Scatter(x=lower_band.index, y=lower_band, mode='lines', fill='tonexty', name=f'{symbol} Lower Band', opacity=0.2))

        fig.update_layout(title="Bollinger Bands", xaxis_title="Date", yaxis_title="Price")

    elif graph_type == 'rsi':
        fig = go.Figure()
        for symbol in valid_symbols:
            series = adj_close[symbol]
            delta = series.diff(1)
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean()
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            fig.add_trace(go.Scatter(x=rsi.index, y=rsi, mode='lines', name=symbol))
            print(gain)
            
            

        fig.add_hline(y=70, line_dash="dash", line_color="red")
        fig.add_hline(y=30, line_dash="dash", line_color="red")
        fig.update_layout(title="Relative Strength Index (RSI)", xaxis_title="Date", yaxis_title="RSI")

    elif graph_type == 'macd':
        fig = go.Figure()
        for symbol in valid_symbols:
            series = adj_close[symbol]
            short_ema = series.ewm(span=12, adjust=False).mean()
            long_ema = series.ewm(span=26, adjust=False).mean()
            macd = short_ema - long_ema
            signal = macd.ewm(span=9, adjust=False).mean()
            fig.add_trace(go.Scatter(x=macd.index, y=macd, mode='lines', name=f'{symbol} MACD'))
            fig.add_trace(go.Scatter(x=signal.index, y=signal, mode='lines', name=f'{symbol} Signal'))

        fig.update_layout(title="MACD (Moving Average Convergence Divergence)", xaxis_title="Date", yaxis_title="Value")

    else:
        return jsonify({"error": "Invalid graph type"}), 400

    # Return the Plotly figure as JSON
    return jsonify(json.loads(fig.to_json()))


if __name__ == '__main__':
    app.run(debug=True)

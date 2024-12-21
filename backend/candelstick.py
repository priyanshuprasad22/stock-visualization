from flask import Flask, jsonify, request
import pandas as pd
import os
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

# Define the directory where CS
directory=r"C:\Users\91790\Desktop\Interactive\backend\Financial Data"

@app.route('/api/stocks/<ticker>/candlestick', methods=['GET'])
def candlestick_chart(ticker):
    try:
        # Define the file path for the stock symbol CSV file
        filepath = os.path.join(directory, f"{ticker}.csv")
        
        if os.path.exists(filepath):
            # Load the CSV file into a DataFrame
            stock_data = pd.read_csv(filepath, skiprows=2, names=['Date', 'Adj_Close', 'Close', 'High', 'Low', 'Open', 'Volume'])
            
            # Remove rows where 'Date' column contains 'Date' or any other non-date values
            stock_data = stock_data[~stock_data['Date'].str.contains('Date', na=False)]
            
            # Convert the 'Date' column to datetime
            stock_data['Date'] = pd.to_datetime(stock_data['Date'].str.split('.').str[0], format='%Y-%m-%d %H:%M:%S')
            
            # Set the 'Date' column as the index
            stock_data.set_index('Date', inplace=True)
            
            # Extract OHLC data for the candlestick chart
            ohlc_data = stock_data[['Open', 'High', 'Low', 'Close', 'Volume']]
            
            # Prepare data for Plotly candlestick chart
            plot_data = {
                'data': [
                    {
                        'x': ohlc_data.index.tolist(),  # Dates
                        'open': ohlc_data['Open'].tolist(),
                        'high': ohlc_data['High'].tolist(),
                        'low': ohlc_data['Low'].tolist(),
                        'close': ohlc_data['Close'].tolist(),
                        'type': 'candlestick',
                        'name': ticker.upper()
                    }
                ],
                'layout': {
                    'title': f'{ticker.upper()} Candlestick Chart',
                    'xaxis': {'title': 'Date'},
                    'yaxis': {'title': 'Price'},
                    'showlegend': False
                }
            }
            
            return jsonify(plot_data)
        
        else:
            return jsonify({"error": f"Data for {ticker} not found in {directory}."}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5002)

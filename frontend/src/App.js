import React, { useState } from "react";
import axios from "axios";
import Plot from "react-plotly.js";

const App = () => {
  const stockSymbols = ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA", "SPY", "NVDA", "META", "NFLX", "AMD"];
  const [symbols, setSymbols] = useState("");
  const [graphType, setGraphType] = useState("daily_returns");
  const [plotData, setPlotData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchGraphData = async () => {
    if (!symbols.trim()) {
      setError("Please enter a stock symbol.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      let response;

      if (graphType === "candlestick") {
        // Fetch candlestick data from the backend
        response = await axios.get(
          `http://127.0.0.1:5002/api/stocks/${symbols}/candlestick`
        );

        // Assuming response.data returns candlestick data in this format
        const { dates, open, high, low, close } = response.data.data[0];
        console.log(response.data.data);

        const plotlyData = [
          {
            x: dates, // Dates for the x-axis
            open: open,
            high: high,
            low: low,
            close: close,
            type: "candlestick", // Specifying candlestick chart type
            name: `${symbols} Candlestick`,
          },
        ];

        const layout = {
          title: `${symbols} Candlestick Chart`,
          xaxis: {
            rangeslider: { visible: false }, // Hides the range slider
            title: "Date",
          },
          yaxis: {
            title: "Price",
          },
        };

        setPlotData({ data: plotlyData, layout });
      } else if (graphType === "trading_volume") {
        // Fetch trading volume data from the backend (Flask API running on port 5003)
        response = await axios.get(
          `http://127.0.0.1:5003/api/stocks/${symbols}/volume`
        );

        // Assuming response.data returns the volume data with x as date and y as volume
        const { x, y } = response.data;

        const plotlyData = [
          {
            x: x, // Dates for the x-axis
            y: y, // Trading volume values
            type: "bar", // Using bar chart for volume
            name: `${symbols} Trading Volume`,
          },
        ];

        const layout = {
          title: `${symbols} Trading Volume`,
          xaxis: {
            title: "Date",
          },
          yaxis: {
            title: "Volume",
          },
        };

        setPlotData({ data: plotlyData, layout });
      } else {
        // Fetch other graph data from the backend
        response = await axios.get("http://127.0.0.1:5000/stock/graph", {
          params: { symbols, graph_type: graphType },
        });

        setPlotData(response.data);
      }
    } catch (err) {
      setError("Failed to fetch graph data. Please check the symbol or backend.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filteredSymbols = stockSymbols.filter(symbol => 
    symbol.toLowerCase().includes(symbols.toLowerCase())
  );

  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <h1>Stock Graph Viewer</h1>
      <div style={{ marginBottom: "20px" }}>
        <label style={{ display: "block", marginBottom: "10px" }}>
          Select Stock Symbol:
        </label>
        <input
          type="text"
          value={symbols}
          onChange={(e) => setSymbols(e.target.value)}
          placeholder="Search symbol (e.g., AAPL)"
          style={{
            padding: "10px",
            width: "100%",
            maxWidth: "400px",
            border: "1px solid #ccc",
            borderRadius: "4px",
          }}
        />
        {symbols && (
          <ul style={{ paddingLeft: "0", marginTop: "10px", border: "1px solid #ccc", borderRadius: "4px" }}>
            {filteredSymbols.map(symbol => (
              <li
                key={symbol}
                onClick={() => setSymbols(symbol)}
                style={{
                  padding: "10px",
                  cursor: "pointer",
                  backgroundColor: "#f9f9f9",
                }}
              >
                {symbol}
              </li>
            ))}
          </ul>
        )}
      </div>
     
      <div style={{ marginBottom: "20px" }}>
        <label style={{ display: "block", marginBottom: "10px" }}>
          Select Graph Type:
        </label>
        <select
          value={graphType}
          onChange={(e) => setGraphType(e.target.value)}
          style={{
            padding: "10px",
            width: "100%",
            maxWidth: "400px",
            border: "1px solid #ccc",
            borderRadius: "4px",
          }}
        >
          <option value="daily_returns">Daily Returns</option>
          <option value="rolling_mean">Rolling Mean</option>
          <option value="bollinger_bands">Bollinger Bands</option>
          <option value="rsi">RSI</option>
          <option value="macd">MACD</option>
          <option value="candlestick">Candlestick</option>
          <option value="trading_volume">Trading Volume</option>
        </select>
      </div>
      <button
        onClick={fetchGraphData}
        style={{
          padding: "10px 20px",
          backgroundColor: "#007bff",
          color: "white",
          border: "none",
          borderRadius: "4px",
          cursor: "pointer",
        }}
      >
        {loading ? "Loading..." : "Fetch Graph"}
      </button>
      {error && <p style={{ color: "red", marginTop: "20px" }}>{error}</p>}
      {plotData && (
        <div style={{ marginTop: "40px" }}>
          <h2>Graph:</h2>
          <Plot
            data={plotData.data}
            layout={plotData.layout}
            style={{ width: "100%" }}
            config={{ responsive: true }}
          />
        </div>
      )}
    </div>
  );
};

export default App;

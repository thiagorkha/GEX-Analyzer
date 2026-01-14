# GEX Analyzer - Quick Start Guide

## Installation

### Prerequisites
- Python 3.11+
- pip or conda

### Step 1: Clone/Setup
```bash
cd Gex-app
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run Application
```bash
python app.py
```

The application will start on `http://localhost:5000`

## Basic Usage

### 1. Access Web Interface
Open your browser and navigate to:
```
http://localhost:5000
```

### 2. Input Data
You have three options:

**Option A: Load Example Data**
- Click "Load Example" button to populate sample OHLC data

**Option B: Manually Enter Data**
- Paste OHLC data as JSON in the OHLC Data textarea
- Example format:
```json
[
  {
    "open": 100.00,
    "high": 102.50,
    "low": 99.50,
    "close": 101.00,
    "volume": 1000000
  },
  ...
]
```

**Option C: With GEX Data**
- Include optional GEX data:
```json
{
  "strike_prices": [95, 100, 105, 110],
  "gamma_values": [0.01, 0.015, 0.012, 0.008],
  "open_interest": [1000, 5000, 4000, 1000]
}
```

### 3. Run Analysis
- Click "Analyze" button
- Wait for results to load

### 4. Review Results
Results are displayed in tabs:
- **Dashboard**: Summary metrics and charts
- **Patterns**: Detected technical patterns
- **Regimes**: Market regime analysis
- **Signals**: Trading recommendations

## Understanding Results

### Dashboard Metrics
- **Current Price**: Latest close price
- **Net GEX**: Positive (bullish) or negative (bearish)
- **24h Volume**: Total trading volume
- **Market Regime**: Bull/Bear/Ranging

### Pattern Analysis
Each pattern shows:
- **Type**: Bullish, Bearish, or Neutral
- **Strength**: 0-100 score
- **Confidence**: 0-1 (0% - 100%)
- **Description**: Pattern interpretation

Example patterns:
- GEX Resistance: Price near resistance level
- GEX Support: Price near support level
- Uptrend: Consistent price increase
- Downtrend: Consistent price decrease

### Regime Analysis
Market regimes with:
- **Type**: Bull/Bear/Ranging/Transition
- **Confidence**: Strength of regime identification
- **Characteristics**:
  - Avg Return: Average return in regime
  - Volatility: Price volatility
  - Avg Volume: Average trading volume

### Trading Signals
Each signal includes:
- **Type**: LONG or SHORT
- **Confidence**: Signal reliability (%)
- **Entry Price**: Suggested entry point
- **Stop Loss**: Risk management level
- **Take Profit**: Target profit level
- **Reason**: Signal explanation

### GEX Interpretation
- **Positive GEX (Bullish)**: Gamma skews support higher prices
- **Negative GEX (Bearish)**: Gamma skews support lower prices
- **Near Zero**: Balanced gamma exposure

## Common Use Cases

### Use Case 1: Trend Analysis
1. Load historical price data
2. Check "Patterns" tab for trend detection
3. Review "Regimes" for confirmation
4. Use "Signals" for trade timing

### Use Case 2: Support/Resistance
1. Input price data
2. Look for "GEX Support" and "GEX Resistance" patterns
3. Check price levels in results
4. Plan trades around these levels

### Use Case 3: Options Analysis
1. Include GEX data with options information
2. Check "Net GEX" in dashboard
3. Positive GEX = bullish setup
4. Negative GEX = bearish setup

### Use Case 4: Risk Management
1. Run analysis on your data
2. Check Stop Loss in trading signals
3. Set stops below signal SL for safety
4. Monitor Take Profit targets

## Tips & Tricks

### Data Quality
- More data points = better analysis
- Ensure OHLC data is chronological
- Check that High > Low for each candle

### Pattern Recognition
- Recent patterns are prioritized
- Confidence scores indicate reliability
- Multiple patterns can confirm signals

### Risk Management
- Never ignore stop losses
- Follow risk-reward ratios
- Position size according to SL distance

### Market Conditions
- Regimes change - update analysis frequently
- Volume patterns matter
- Combine multiple indicators

## API Usage (Python)

```python
import requests
import json

# API endpoint
url = "http://localhost:5000/api/analyze"

# Prepare data
data = {
    "ohlc_data": [
        {"open": 100, "high": 105, "low": 98, "close": 102, "volume": 1000}
    ]
}

# Send request
response = requests.post(url, json=data)

# Parse results
results = response.json()
print(results)
```

## API Usage (cURL)

```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "ohlc_data": [
      {"open": 100, "high": 105, "low": 98, "close": 102, "volume": 1000}
    ]
  }'
```

## Troubleshooting

### Application won't start
```bash
# Check Python version
python --version  # Should be 3.11+

# Check dependencies
pip list | grep -E "Flask|pandas"

# Try installing dependencies again
pip install -r requirements.txt
```

### Invalid JSON error
- Ensure JSON is properly formatted
- Use JSON validator: https://jsonlint.com
- Check quotes are correct (not smart quotes)

### No patterns detected
- May need more data points (minimum 2)
- Prices may not have sufficient movement
- Check data quality

### API connection error
- Ensure server is running
- Check port 5000 is not in use
- Try http://localhost:5000/api/health

## Next Steps

1. **Read Technical Documentation**: TECHNICAL_DOCS.md
2. **Run Tests**: pytest tests/
3. **Deploy**: See DEPLOY_RENDER.md
4. **Advanced**: Customize strategies in backend/strategies/engine.py

## Support & Documentation

- Technical Details: `TECHNICAL_DOCS.md`
- Testing Guide: `TESTING_GUIDE.md`
- Deployment: `DEPLOY_RENDER.md`
- Full README: `README.md`


# GEX Analyzer - Technical Documentation

## Overview

GEX Analyzer is an advanced technical analysis platform for gamma exposure (GEX) analysis and trading strategy evaluation. It combines options market analysis with technical pattern recognition and market regime identification.

## Architecture

### Backend Architecture

```
backend/
├── config.py          # Configuration management
├── data/
│   └── validator.py   # Data validation module
├── gex/
│   ├── calculator.py  # GEX calculation engine
│   ├── patterns.py    # Pattern detection
│   └── regime.py      # Market regime analysis
├── strategies/
│   └── engine.py      # Trading strategy engine
└── api/
    └── routes.py      # Flask API endpoints
```

### Core Modules

#### 1. GEX Calculator (`backend/gex/calculator.py`)

Calculates Gamma Exposure (GEX) from options data.

**Key Methods:**
- `calculate_gex()`: Main GEX calculation
- `calculate_implied_volatility()`: Calculate IV using Newton-Raphson
- `calculate_delta()`: Black-Scholes delta
- `calculate_gamma()`: Black-Scholes gamma
- `analyze_gex_levels()`: Identify significant GEX barriers

**Algorithm:**
- Uses Black-Scholes model for pricing
- Weights gamma by distance from spot price
- Separates long and short gamma exposure

#### 2. Pattern Detector (`backend/gex/patterns.py`)

Identifies technical patterns in market data.

**Pattern Types:**
- `BULLISH`: Upward moving patterns
- `BEARISH`: Downward moving patterns
- `NEUTRAL`: Sideways movement
- `DIVERGENCE`: Price-indicator divergence

**Detection Methods:**
- GEX resistance patterns
- GEX support patterns
- Volatility patterns
- Trend patterns

#### 3. Regime Analyzer (`backend/gex/regime.py`)

Identifies and analyzes market regimes.

**Regime Types:**
- `BULL`: Bullish market regime
- `BEAR`: Bearish market regime
- `RANGING`: Sideways market
- `TRANSITION`: Transitioning between regimes

**Characteristics:**
- Average return calculation
- Volatility measurement
- Volume analysis
- Confidence scoring

#### 4. Strategy Engine (`backend/strategies/engine.py`)

Generates trading signals and performs backtesting.

**Signal Generation:**
- Evaluates GEX conditions
- Analyzes pattern signals
- Incorporates regime analysis
- Calculates risk-reward ratios

**Backtest Features:**
- Win/loss ratio calculation
- Return analysis
- Signal performance metrics

#### 5. Data Validator (`backend/data/validator.py`)

Validates and cleans market data.

**Validations:**
- OHLC data structure
- Price relationships (H > L, H > O/C, etc.)
- Volume checks
- Parameter validation

## API Endpoints

### Analysis Endpoint
```
POST /api/analyze
```
**Request:**
```json
{
  "ohlc_data": [...],
  "strike_prices": [...],
  "gamma_values": [...],
  "open_interest": [...]
}
```

**Response:**
```json
{
  "status": "success",
  "summary": {...},
  "gex_analysis": {...},
  "patterns": [...],
  "regimes": [...],
  "signals": [...]
}
```

### GEX Calculator Endpoint
```
POST /api/calculator
```
Dedicated GEX calculation endpoint.

### Pattern Detection Endpoint
```
POST /api/patterns
```
Detects patterns in provided OHLC data.

### Regime Analysis Endpoint
```
POST /api/regime
```
Analyzes market regimes.

### Signal Generation Endpoint
```
POST /api/signals
```
Generates trading signals.

## Black-Scholes Model

### Formula

**d1 = (ln(S/K) + (r + σ²/2)T) / (σ√T)**

**d2 = d1 - σ√T**

**Call Price = S × N(d1) - K × e^(-rT) × N(d2)**

**Put Price = K × e^(-rT) × N(-d2) - S × N(-d1)**

Where:
- S = Spot price
- K = Strike price
- r = Risk-free rate
- σ = Volatility
- T = Time to expiry
- N() = Cumulative normal distribution

### Greeks

**Delta = ∂C/∂S = N(d1)** (for calls)

**Gamma = ∂²C/∂S² = N'(d1) / (S × σ × √T)**

## Gamma Exposure Calculation

GEX is calculated as:

**GEX = Σ (Gamma × Open Interest × Distance Weight)**

**Distance Weight = 1 / (1 + |Strike - Spot| / Spot)**

### Interpretation

- **Positive GEX**: Market makers are short gamma (bullish conditions)
- **Negative GEX**: Market makers are long gamma (bearish conditions)
- **High Absolute GEX**: Strong gamma barriers

## Pattern Detection Algorithm

### Resistance Detection
```python
recent_high = max(highs[i-5:i])
if close[i] > recent_high * 0.95:
    strength = (close[i] / recent_high - 1) * 100
    # Create resistance pattern
```

### Support Detection
```python
recent_low = min(lows[i-5:i])
if close[i] < recent_low * 1.05:
    strength = (1 - close[i] / recent_low) * 100
    # Create support pattern
```

### Trend Detection
```python
if close[-1] > close[-5]:
    # Uptrend (bullish)
elif close[-1] < close[-5]:
    # Downtrend (bearish)
else:
    # Ranging
```

## Regime Analysis Algorithm

1. **Calculate Indicators**
   - Rolling volatility
   - Average returns
   - Volume moving average

2. **Identify Regime Type**
   - Bull: positive recent returns
   - Bear: negative recent returns
   - Ranging: near-zero returns

3. **Calculate Characteristics**
   - Average return
   - Volatility
   - Average volume
   - Confidence score

4. **Confidence Scoring**
```
Volatility Score = 1 - min(1, volatility * 10)
Consistency Score = |avg_return| / (std_return + ε)
Confidence = (Volatility Score + min(1, Consistency Score)) / 2
```

## Data Flow

```
User Input
    ↓
Data Validation
    ↓
API Request Processing
    ↓
├─ GEX Calculation
├─ Pattern Detection
├─ Regime Analysis
├─ Strategy Evaluation
    ↓
Signal Generation
    ↓
Response Formatting
    ↓
Frontend Visualization
```

## Performance Considerations

- **Data Validation**: O(n) complexity
- **Pattern Detection**: O(n × window_size)
- **Regime Analysis**: O(n × lookback_period)
- **GEX Calculation**: O(strikes × spot_prices)
- **Black-Scholes**: O(1) per option

## Error Handling

- Input validation with detailed error messages
- Graceful handling of missing data
- Fallback values for invalid calculations
- Comprehensive logging for debugging

## Configuration

See `backend/config.py` for:
- Database settings
- API limits
- File upload sizes
- Debug modes
- Environment-specific settings

## Dependencies

See `requirements.txt` for full list:
- Flask 3.0.0
- Pandas 2.0.3
- NumPy 1.24.3
- Scipy (for optimization)
- Pytest 7.4.0 (testing)


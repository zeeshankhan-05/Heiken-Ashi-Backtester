# Heiken-Ashi Trading Strategy Backtester

A comprehensive Python-based backtesting system that implements a multi-condition trading strategy using Heiken-Ashi candlesticks, moving averages, and MACD indicators to evaluate historical stock performance.

## 🎯 Project Overview

This backtesting framework tests a sophisticated trading strategy that combines:
- **Heiken-Ashi candlesticks** for trend smoothing and signal generation
- **Moving average crossovers** (50-day and 100-day) for trend confirmation
- **MACD histogram analysis** for momentum validation
- **Day-of-week restrictions** for strategic entry timing

The system simulates real trading conditions with $10,000 position limits and tracks comprehensive performance metrics including total returns, win rates, maximum drawdown, and trade-by-trade analysis.

## 🏗️ Architecture

### Core Components

- **`data_loader.py`** - Fetches historical data from Yahoo Finance and calculates Heiken-Ashi indicators
- **`strategy.py`** - Implements buy/sell signal logic based on multi-condition rules
- **`backtest.py`** - Executes trades, manages portfolio, and calculates performance metrics

### Trading Strategy Logic

**Buy Conditions (ALL must be true):**
- Trading day is Monday, Wednesday, or Friday
- Current position value < $10,000 (position limit)
- No sell signal active on the same day

**Sell Conditions (ALL must be true):**
- Heiken-Ashi close < 100-day moving average
- 50-day moving average is flat or declining
- MACD histogram is negative or decreasing

## 📊 Supported Stock Universe

The system is designed to test on 24 technology and growth stocks:
```
TSM, QCOM, SPGI, TJX, ADI, WM, MCK, SHW, RSG, TEAM, 
FICO, RMD, MPWR, TSCO, TYL, EME, JBHT, MANH, SAIA, 
FSS, UFPT, WS, WTTR, VMD
```

## 🚀 Quick Start

### Prerequisites

```bash
pip install pandas numpy matplotlib yfinance
```

### Usage

1. **Fetch and Process Data**
   ```bash
   python data_loader.py
   ```
   This downloads historical data and calculates all technical indicators.

2. **Generate Trading Signals**
   ```bash
   python strategy.py
   ```
   This applies the trading rules and generates buy/sell signals.

3. **Run Backtest**
   ```bash
   python backtest.py
   ```
   This executes the trades and generates performance reports.

### Example Output

```
=== BACKTEST SUMMARY for TYL ===
Initial Cash: $100,000.00
Final Portfolio Value: $128,450.00
Total Return: 28.45%
Maximum Drawdown: -12.3%
Number of Trades: 47
Win Rate: 68.1%
Average Holding Period: 23.4 days
```

## 📈 Performance Metrics

The backtester calculates comprehensive performance analytics:

- **Total Return** - Overall portfolio performance vs buy-and-hold
- **Maximum Drawdown** - Largest peak-to-trough decline
- **Win Rate** - Percentage of profitable trades
- **Sharpe Ratio** - Risk-adjusted returns
- **Trade Statistics** - Entry/exit prices, holding periods, P&L per trade

## 🔧 Configuration

### Modifying Parameters

Key parameters can be adjusted in the respective files:

```python
# Position sizing (backtest.py)
POSITION_SIZE = 10000  # $10K per trade

# Moving average periods (data_loader.py)
SHORT_MA = 50   # 10-week equivalent
LONG_MA = 100   # 20-week equivalent

# MACD parameters (data_loader.py)
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
```

### Adding New Stocks

Update the ticker list in `data_loader.py`:
```python
TICKERS = ['AAPL', 'MSFT', 'GOOGL']  # Add your symbols here
```

## 📁 File Structure

```
heiken-ashi-backtester/
├── data_loader.py          # Data fetching and indicator calculation
├── strategy.py             # Trading signal generation
├── backtest.py            # Portfolio simulation and performance analysis
├── stock_backtesting_algorithm.py  # Alternative weekly strategy implementation
├── indicators_*.csv       # Generated technical indicator data
├── signals_*.csv         # Generated buy/sell signals
├── backtest_*.csv        # Detailed backtest results
└── README.md
```

## 🎯 Key Features

- **Heiken-Ashi Integration** - Reduces market noise for cleaner trend identification
- **Multi-Condition Logic** - Combines trend, momentum, and timing filters
- **Risk Management** - Position sizing limits and systematic exit rules
- **Comprehensive Analytics** - Detailed trade logs and performance metrics
- **Extensible Design** - Easy to modify rules and add new indicators

## 🔍 Technical Implementation

### Heiken-Ashi Calculation
```python
HA_Close = (Open + High + Low + Close) / 4
HA_Open = (Previous_HA_Open + Previous_HA_Close) / 2
HA_High = max(High, HA_Open, HA_Close)
HA_Low = min(Low, HA_Open, HA_Close)
```

### Signal Generation
The strategy uses a strict AND logic for entries and exits, ensuring high-confidence trades while maintaining systematic risk management through position limits and day-of-week restrictions.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## ⚠️ Disclaimer

This backtesting system is for educational and research purposes only. Past performance does not guarantee future results. Always conduct your own research and consider consulting with a financial advisor before making investment decisions.

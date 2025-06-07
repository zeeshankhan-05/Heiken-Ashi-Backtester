import yfinance as yf
import pandas as pd
from datetime import datetime

TICKERS = ['MPWR', 'TSCO', 'TYL']

START_DATE = "2022-01-01"
END_DATE = datetime.today().strftime('%Y-%m-%d')

def fetch_stock_data(ticker):
    """Fetch and clean historical stock data for a given ticker"""
    df = yf.download(ticker, start=START_DATE, end=END_DATE, group_by='column')
    df.columns.name = None  # Flatten MultiIndex
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.loc[:, ~df.columns.duplicated()]
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    df.dropna(inplace=True)
    df['Ticker'] = ticker
    return df

def fetch_all():
    """Loop through all tickers and collect their historical data"""
    all_data = {}
    for ticker in TICKERS:
        print(f"Fetching {ticker}...")
        try:
            df = fetch_stock_data(ticker)
            all_data[ticker] = df
            print(f"{ticker}: {len(df)} days of data")
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
    return all_data

def calculate_heiken_ashi(df):
    """Calculate Heiken Ashi candles for a given DataFrame"""
    ha_df = df.copy()
    
    # Convert to numeric to handle any string data
    high = pd.to_numeric(df['High'], errors='coerce')
    low = pd.to_numeric(df['Low'], errors='coerce')
    open_ = pd.to_numeric(df['Open'], errors='coerce')
    close = pd.to_numeric(df['Close'], errors='coerce')

    # Calculate HA values
    ha_close = (open_ + high + low + close) / 4
    
    # Initialize HA Open
    ha_open = [(open_.iloc[0] + close.iloc[0]) / 2]
    for i in range(1, len(df)):
        prev_ha_open = ha_open[i - 1]
        prev_ha_close = ha_close.iloc[i - 1]
        ha_open.append((prev_ha_open + prev_ha_close) / 2)

    # Create HA DataFrame
    ha_df['HA_Close'] = ha_close
    ha_df['HA_Open'] = pd.Series(ha_open, index=ha_df.index)
    ha_df['HA_High'] = pd.concat([high, ha_df['HA_Open'], ha_df['HA_Close']], axis=1).max(axis=1)
    ha_df['HA_Low'] = pd.concat([low, ha_df['HA_Open'], ha_df['HA_Close']], axis=1).min(axis=1)

    return ha_df

def add_moving_averages(df):
    """Add 50-day and 100-day moving averages to HA data"""
    df['HA_50_MA'] = df['HA_Close'].rolling(window=50).mean()
    df['HA_100_MA'] = df['HA_Close'].rolling(window=100).mean()
    return df

def calculate_macd(df):
    """Calculate MACD indicators using standard Close prices"""
    short_ema = df['Close'].ewm(span=12, adjust=False).mean()
    long_ema = df['Close'].ewm(span=26, adjust=False).mean()
    macd_line = short_ema - long_ema
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    macd_histogram = macd_line - signal_line

    return pd.DataFrame({
        'MACD_Line': macd_line,
        'Signal_Line': signal_line,
        'MACD_Hist': macd_histogram
    }, index=df.index)

def process_ticker_data(ticker, raw_df):
    """Process a single ticker's data through the full pipeline"""
    print(f"\nProcessing {ticker}...")
    
    # Calculate Heiken Ashi (includes original OHLC + HA values)
    ha_df = calculate_heiken_ashi(raw_df)
    
    # Add moving averages based on HA Close
    ha_df = add_moving_averages(ha_df)
    
    # Calculate MACD based on standard Close
    macd_df = calculate_macd(raw_df)
    
    # Combine everything - this preserves the standard Close price
    final_df = pd.concat([ha_df, macd_df], axis=1)
    
    # Ensure we have the standard Close price for trading
    if 'Close' not in final_df.columns:
        final_df['Close'] = raw_df['Close']
    
    print(f"{ticker} processed: {len(final_df)} rows")
    print(f"  Columns: {list(final_df.columns)}")
    
    return final_df

if __name__ == "__main__":
    print("Starting data fetch and processing...")
    
    data = fetch_all()
    
    if not data:
        print("No data fetched. Exiting.")
        exit(1)
    
    for ticker, raw_df in data.items():
        try:
            processed_df = process_ticker_data(ticker, raw_df)
            
            filename = f"indicators_{ticker}.csv"
            processed_df.to_csv(filename)
            print(f"Saved {filename}")
        
            sample_cols = ['Close', 'HA_Close', 'HA_50_MA', 'HA_100_MA', 'MACD_Hist']
            available_cols = [col for col in sample_cols if col in processed_df.columns]
            
            print(f"\nSample data for {ticker}:")
            print(processed_df[available_cols].dropna().tail())
            
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
    
    print(f"\n{'='*50}")
    print("Data processing complete!")
    print("Next steps:")
    print("1. Run strategy.py to generate buy/sell signals")
    print("2. Run backtest.py to execute the backtest")
    print("3. Check the results!")
    
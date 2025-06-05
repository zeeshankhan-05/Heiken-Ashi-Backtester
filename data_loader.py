import yfinance as yf
import pandas as pd
from datetime import datetime

TICKERS = ['MPWR, TSCO, TYL']

START_DATE = "2022-01-01"
END_DATE = datetime.today().strftime('%Y-%m-%d')

# Fetch and clean historical stock data for a given ticker
def fetch_stock_data(ticker):
    df = yf.download(ticker, start=START_DATE, end=END_DATE, group_by='column')
    df.columns.name = None  # Flatten MultiIndex
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.loc[:, ~df.columns.duplicated()]
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    df.dropna(inplace=True)
    df['Ticker'] = ticker
    return df

# Loop through all tickers and collect their historical data
def fetch_all():
    all_data = {}
    for ticker in TICKERS:
        print(f"Fetching {ticker}...")
        try:
            df = fetch_stock_data(ticker)
            all_data[ticker] = df
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
    return all_data


# Calculate Heiken Ashi candles for a given DataFrame
def calculate_heiken_ashi(df):
    ha_df = df.copy()
    
    print("\nDEBUG - DataFrame Columns:", df.columns)
    print("DEBUG - Type of df['High']:", type(df['High']))
    print("DEBUG - Sample df['High']:", df['High'].head())
    
    high = pd.to_numeric(df['High'], errors='coerce')
    low = pd.to_numeric(df['Low'], errors='coerce')
    open_ = pd.to_numeric(df['Open'], errors='coerce')
    close = pd.to_numeric(df['Close'], errors='coerce')

    ha_close = (open_ + high + low + close) / 4
    ha_open = [(open_.iloc[0] + close.iloc[0]) / 2]

    for i in range(1, len(df)):
        prev_ha_open = ha_open[i - 1]
        prev_ha_close = ha_close.iloc[i - 1]
        ha_open.append((prev_ha_open + prev_ha_close) / 2)

    ha_df['HA_Close'] = ha_close
    ha_df['HA_Open'] = pd.Series(ha_open, index=ha_df.index)

    ha_df['HA_High'] = pd.concat([high, ha_df['HA_Open'], ha_df['HA_Close']], axis=1).max(axis=1)
    ha_df['HA_Low'] = pd.concat([low, ha_df['HA_Open'], ha_df['HA_Close']], axis=1).min(axis=1)

    return ha_df[['HA_Open', 'HA_High', 'HA_Low', 'HA_Close']]

# Add 50-day and 100-day moving averages to HA data
def add_moving_averages(ha_df):
    ha_df['HA_50_MA'] = ha_df['HA_Close'].rolling(window=50).mean()
    ha_df['HA_100_MA'] = ha_df['HA_Close'].rolling(window=100).mean()
    return ha_df

# Calculate MACD indicators
def calculate_macd(df):
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

# Main process
if __name__ == "__main__":
    data = fetch_all()
    for ticker, raw_df in data.items():
        # Work only with a clean OHLC copy
        ohlc_df = raw_df[['Open', 'High', 'Low', 'Close']].copy()

        ha_df = calculate_heiken_ashi(ohlc_df)
        ha_df = add_moving_averages(ha_df)

        macd_df = calculate_macd(ohlc_df)

        # Combine HA + MA + MACD into one DataFrame
        ha_df = pd.concat([ha_df, macd_df], axis=1)

        # Save final indicators to CSV
        ha_df.to_csv(f"indicators_{ticker}.csv")

        print(f"\n{ticker} Indicators Sample:")
        print(ha_df[['HA_Close', 'HA_50_MA', 'HA_100_MA', 'MACD_Hist']].dropna().head())

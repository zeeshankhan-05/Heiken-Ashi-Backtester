import yfinance as yf
import pandas as pd
from datetime import datetime

TICKERS = ['TSM', 'QCOM', 'SHW']

START_DATE = "2020-01-01"
END_DATE = datetime.today().strftime('%Y-%m-%d')

# Fetch and clean historical stock data for a given ticker
def fetch_stock_data(ticker):
    df = yf.download(ticker, start=START_DATE, end=END_DATE)
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
    ''''
    Returns a DataFrame with Heiken Ashi Open, High, Low, Close columns
    '''
    
    ha_df = df.copy()

    ha_df['HA_Close'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4

    ha_open = [(df['Open'].iloc[0] + df['Close'].iloc[0]) / 2]
    for i in range(1, len(df)):
        prev_ha_open = ha_open[i - 1]
        prev_ha_close = ha_df['HA_Close'].iloc[i - 1]
        ha_open.append((prev_ha_open + prev_ha_close) / 2)
    ha_df['HA_Open'] = pd.Series(ha_open, index=ha_df.index, dtype='float64')

    for col in ['High', 'HA_Open', 'HA_Close']:
        ha_df[col] = ha_df[col].apply(lambda x: x[0] if isinstance(x, (list, tuple)) else x)
        
    ha_df['HA_High'] = ha_df[['High', 'HA_Open', 'HA_Close']].max(axis=1)
    ha_df['HA_Low'] = ha_df[['Low', 'HA_Open', 'HA_Close']].min(axis=1)

    return ha_df[['HA_Open', 'HA_High', 'HA_Low', 'HA_Close']]

if __name__ == "__main__":
    """
    Fetches data for all tickers, calculate Heiken Ashi candles, print sample, and save to CSV
    """
    
    data = fetch_all()
    for ticker, df in data.items():
        ha_df = calculate_heiken_ashi(df)
        print(f"\n{ticker} Heiken Ashi sample:")
        print(ha_df.head())
        ha_df.to_csv(f"heiken_ashi_{ticker}.csv")
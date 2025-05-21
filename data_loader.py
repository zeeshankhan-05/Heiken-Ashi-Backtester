import yfinance as yf
import pandas as pd
from datetime import datetime

# Stocks to test
TICKERS = ['TSM', 'QCOM', 'SHW']

# Date range
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

# Run the script: fetch data and display sample output for each ticker
if __name__ == "__main__":
    data = fetch_all()
    for ticker, df in data.items():
        print(f"\n{ticker} data sample:")
        print(df.head())

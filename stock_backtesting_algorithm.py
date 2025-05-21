import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def backtest_strategy(data,ticker, max_shares=20):
    """
    Backtests a strategy that:
      - Buys one share every week.
      - Sells the entire accumulated position when two of the following three conditions are met:
          1. The weekly close is below the 20-week moving average.
          2. The 10-week moving average is flat or decreasing compared to the previous week.
          3. The MACD is negative OR it is lower than the previous week's MACD.
    
    Parameters:
      data (pd.DataFrame): DataFrame with at least 'Date' and 'Close' columns.
    
    Returns:
      weekly (pd.DataFrame): The weekly resampled price data with indicators.
      signals (list): A list of tuples with signal details (date, action, price, cumulative shares).
      trades (list): A list of dictionaries describing each complete trade.
    """
    
    # Ensure data is sorted by date and convert Date column to datetime.
    data['Date'] = pd.to_datetime(data['Date'])
    data.sort_values('Date', inplace=True)
    data.set_index('Date', inplace=True)
    
    # Resample daily data to weekly data (taking the last price of Friday of each week)
    # Adjust the resampling rule if needed.
    weekly = data['Close'].resample('W-FRI').last()

    # Calculate indicators:
    # 1. 21-week Simple Moving Average (SMA)
    weekly.reset_index(inplace=True)
    weekly.rename(columns={ticker: 'Close'}, inplace=True)
    print("Weekly columns before adding indicators:", weekly.columns)
    
    weekly['MA21'] = weekly['Close'].rolling(window=21).mean()
    weekly['MA10'] = weekly['Close'].rolling(window=10).mean() 
    # 2. 10-week SMA and its previous value (slope check)
    weekly['MA10_prev'] = weekly['MA10'].shift(1)
    
    # 3. MACD computed as the difference between 12-week EMA and 50-week EMA.
    weekly['EMA12'] = weekly['Close'].ewm(span=12, adjust=False).mean()
    weekly['EMA20'] = weekly['Close'].ewm(span=20, adjust=False).mean()
    weekly['MACD'] = weekly['EMA12'] - weekly['EMA20']
    weekly['MACD_prev'] = weekly['MACD'].shift(1)
    
    # Define each sell condition:
    # Condition 1: Price drops below the 21-week MA.
    weekly['cond1'] = weekly['Close'] <= weekly['MA10']
    
    weekly['cond2'] = weekly['MA10'] <= weekly['MA10_prev']
    
    weekly['cond3'] = weekly['MA10'] <= weekly['MA21']
    
    # weekly['cond3'] = (weekly['MACD'] < 0) | (weekly['MACD'] < weekly['MACD_prev'])
    

    # Initialize the backtest simulation variables.
    signals = []  # To record every buy and sell signal (date, action, price, cumulative shares)
    trades = []   # To record details for each complete trade cycle.
    position = 0  # Cumulative number of shares held.
    total_cost = 0.0  # Total cost basis of the accumulated shares.
    entry_date = None  # Records when the current accumulation cycle started.
    # buy_week = True
    portfolio=0
    
    for date, row in weekly.iloc[21:].iterrows():  # Start looping from the 22nd row (index 21)
        
        if not row['cond1'] and not row['cond2'] and not row['cond3'] and portfolio < max_shares:  # Assuming 'MA10' is the column for the 10-week moving average
            buy_price = row['Close']
            position += 1
            total_cost += buy_price
            signals.append((date, 'BUY', buy_price, position))
            portfolio += 1
        # If this is the first week in the cycle, mark the entry_date.
        if entry_date is None:
            entry_date = date

        # Only check sell signals if we have enough history so that the indicators are non-NaN.
        if pd.notna(row['cond1']) and pd.notna(row['cond2']) and pd.notna(row['cond3']):
            # Count how many conditions are met.
            conditions_met = sum([row['cond1'], row['cond2'], row['cond3']])
            if conditions_met > 0 and position > 0:
                sell_price = row['Close']
                signals.append((date, 'SELL', sell_price, position, conditions_met))
                profit = (position * sell_price) - total_cost
                trades.append({
                    'entry_date': entry_date,
                    'exit_date': date,
                    'shares': position,
                    'sell_price': sell_price,
                    'proceeds': position * sell_price,
                    'profit': profit
                })
                # Reset the position and cost basis for the next cycle.
                position = 0
                total_cost = 0.0
                entry_date = None
                portfolio = 0
    if position > 0:
        last_date = weekly.index[-1]
        last_close = weekly.iloc[-1]['Close']
        signals.append((last_date, 'SELL', last_close, position))
        profit = position * last_close - total_cost
        trades.append({
            'entry_date': entry_date,
            'exit_date': last_date,
            'shares': position,
            'sell_price': last_close,
            'proceeds': position * last_close,
            'profit': profit
        })
        
    return weekly, signals, trades

if __name__ == "__main__":
    ticker = 'WM'
    try:
        # Read data from CSV. Adjust the file path if necessary.
        # data = pd.read_csv('stock_data.csv')
    
        data = yf.download(ticker, start='2021-02-06', end='2025-4-10')
        data.reset_index(inplace=True)
        data = data[['Date', 'Close']]
        
    except Exception as e:
        print("Error reading 'stock_data.csv'. Please ensure the file exists and has columns 'Date' and 'Close'.")
        raise e

    # Run the backtest.
    max_shares=15
    weekly_df, signals, trade_log = backtest_strategy(data, ticker, max_shares)
    
    # Display signals.
    print("Trading Signals:")
    for signal in signals:
        # Each signal is a tuple: (date, 'BUY'/'SELL', price, cumulative_position)
        print(signal)
    # Plot the price with buy and sell signals
    # Plot the price with buy and sell signals
    plt.figure(figsize=(16, 8))
    start_date = datetime(2021, 2, 6)
    filtered_weekly_df = weekly_df[weekly_df['Date'] >= start_date]

    # Plot the filtered data
    plt.plot(filtered_weekly_df['Date'], filtered_weekly_df['Close'], label='Price')
    
    # Add buy and sell signals
    for signal in signals:
        weeks_to_add, action, price, *_ = signal
        if action == 'BUY':
            # plt.plot(datetime(2018, 2, 6) + timedelta(weeks=weeks_to_add), marker='^', color='green', markersize=8)
            plt.plot(start_date + timedelta(weeks=weeks_to_add+1), 0.99*price, marker='^', color='green', markersize=5)
        elif action == 'SELL':
            plt.plot(start_date + timedelta(weeks=weeks_to_add+1), 0.99*price, marker='^', color='red', markersize=5)

    plt.title(f'{ticker} Price with Buy/Sell Signals')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'trading_signals_{ticker}_{max_shares}.png')
    plt.close()

import pandas as pd

def backtest_strategy(df, ticker, initial_cash=100000):
    """Backtest trading strategy using Heikin-Ashi data"""
    df = df.copy()
    
    # Initialize variables
    cash = initial_cash
    position = 0
    entry_price = 0
    trades = []
    
    # Add tracking columns
    df['Cash'] = 0.0
    df['Holdings'] = 0.0
    df['Total_Value'] = 0.0
    
    for i in range(len(df)):
        date = df.index[i]
        price = df['HA_Open'].iloc[i]
        
        # Skip if price is NaN
        if pd.isna(price):
            continue
        
        # Buy signal - invest $10,000 if not holding
        if df['Buy_Signal'].iloc[i] and position == 0:
            shares_to_buy = int(10000 // price)
            cost = shares_to_buy * price
            
            if cash >= cost and shares_to_buy > 0:
                position = shares_to_buy
                entry_price = price
                cash -= cost
                
                trades.append({
                    'Type': 'Buy',
                    'Date': date,
                    'Price': price,
                    'Shares': shares_to_buy,
                    'Cash_After': cash
                })
        
        # Sell signal - sell all shares if holding
        elif df['Sell_Signal'].iloc[i] and position > 0:
            proceeds = position * price
            profit = proceeds - (position * entry_price)
            cash += proceeds
            
            trades.append({
                'Type': 'Sell',
                'Date': date,
                'Price': price,
                'Shares': position,
                'Cash_After': cash,
                'Profit': profit
            })
            
            position = 0
            entry_price = 0
        
        # Track daily portfolio value
        df.loc[date, 'Cash'] = cash
        df.loc[date, 'Holdings'] = position * price
        df.loc[date, 'Total_Value'] = cash + (position * price)
    
    # Final liquidation if still holding
    if position > 0:
        last_price = df['HA_Open'].iloc[-1]
        if not pd.isna(last_price):
            proceeds = position * last_price
            profit = proceeds - (position * entry_price)
            cash += proceeds
            
            trades.append({
                'Type': 'Final Sell',
                'Date': df.index[-1],
                'Price': last_price,
                'Shares': position,
                'Cash_After': cash,
                'Profit': profit
            })
            
            df.loc[df.index[-1], 'Cash'] = cash
            df.loc[df.index[-1], 'Holdings'] = 0
            df.loc[df.index[-1], 'Total_Value'] = cash
    
    return df, trades

def print_summary(ticker, df, trades, initial_cash=100000):
    """Print backtest summary"""
    final_value = df['Total_Value'].iloc[-1]
    total_return = ((final_value - initial_cash) / initial_cash) * 100
    
    print(f"\n{'='*50}")
    print(f"BACKTEST SUMMARY for {ticker}")
    print(f"{'='*50}")
    print(f"Initial Cash: ${initial_cash:,.2f}")
    print(f"Final Portfolio Value: ${final_value:,.2f}")
    print(f"Total Return: {total_return:.2f}%")
    print(f"Number of Trades: {len(trades)}")
    
    if trades:
        buy_trades = [t for t in trades if t['Type'] == 'Buy']
        sell_trades = [t for t in trades if t['Type'] in ['Sell', 'Final Sell']]
        total_profit = sum(t.get('Profit', 0) for t in sell_trades)
        
        print(f"Buy Trades: {len(buy_trades)}")
        print(f"Sell Trades: {len(sell_trades)}")
        print(f"Total Profit: ${total_profit:,.2f}")

if __name__ == "__main__":
    ticker = "TYL"
    
    try:
        # Load data and run backtest
        df = pd.read_csv(f"signals_{ticker}.csv", index_col=0, parse_dates=True)
        df, trades = backtest_strategy(df, ticker)
        
        print_summary(ticker, df, trades)
        
        df.to_csv(f"backtest_{ticker}.csv")
        print(f"\nResults saved to: backtest_{ticker}.csv")
        
    except FileNotFoundError:
        print(f"Error: Could not find signals_{ticker}.csv")
    except Exception as e:
        print(f"Error: {e}")
        
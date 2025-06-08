import pandas as pd
import numpy as np

def backtest_strategy(df, ticker, initial_cash=100000):
    """
    Backtest trading strategy using Heikin-Ashi signals but standard Close prices for trades
    """
    df = df.copy()
    
    cash = initial_cash
    position = 0
    entry_price = 0
    trades = []
    
    df['Cash'] = 0.0
    df['Holdings'] = 0.0
    df['Total_Value'] = 0.0
    
    for i in range(len(df)):
        date = df.index[i]
        
        trade_price = df['Close'].iloc[i]
        
        # Skip if price is NaN
        if pd.isna(trade_price):
            continue
        
        # Buy signal - invest $10,000 if not holding
        if df['Buy_Signal'].iloc[i] and position == 0:
            shares_to_buy = int(10000 // trade_price)
            cost = shares_to_buy * trade_price
            
            if cash >= cost and shares_to_buy > 0:
                position = shares_to_buy
                entry_price = trade_price
                cash -= cost
                
                trades.append({
                    'Type': 'Buy',
                    'Date': date,
                    'Price': trade_price,  # Standard Close price
                    'Shares': shares_to_buy,
                    'Cash_After': cash
                })
                
                print(f"BUY: {date.date()} - {shares_to_buy} shares at ${trade_price:.2f}")
        
        # Sell signal - sell all shares if holding
        elif df['Sell_Signal'].iloc[i] and position > 0:
            proceeds = position * trade_price
            profit = proceeds - (position * entry_price)
            cash += proceeds
            
            trades.append({
                'Type': 'Sell',
                'Date': date,
                'Price': trade_price,  # Standard Close price
                'Shares': position,
                'Cash_After': cash,
                'Profit': profit
            })
            
            print(f"SELL: {date.date()} - {position} shares at ${trade_price:.2f} (Profit: ${profit:.2f})")
            
            position = 0
            entry_price = 0
        
        # Track daily portfolio value
        df.loc[date, 'Cash'] = cash
        df.loc[date, 'Holdings'] = position * trade_price
        df.loc[date, 'Total_Value'] = cash + (position * trade_price)
    
    # Final liquidation if still holding
    if position > 0:
        last_price = df['Close'].iloc[-1]
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
            
            print(f"FINAL SELL: {df.index[-1].date()} - {position} shares at ${last_price:.2f} (Final Liquidation)")
            
            # Update the final row with liquidated values
            df.loc[df.index[-1], 'Cash'] = cash
            df.loc[df.index[-1], 'Holdings'] = 0
            df.loc[df.index[-1], 'Total_Value'] = cash
            
            # Reset position tracking
            position = 0
            entry_price = 0
        else:
            print(f"WARNING: Cannot liquidate position - final price is NaN")
            # If unable to get a valid price, mark holdings at 0 value
            df.loc[df.index[-1], 'Holdings'] = 0
            df.loc[df.index[-1], 'Total_Value'] = cash

    # Final liquidation summary
    print(f"\n=== FINAL LIQUIDATION SUMMARY ===")
    if position == 0:
        print("All positions successfully liquidated")
        print(f"Final cash balance: ${cash:,.2f}")
    else:
        print(f"WARNING: {position} shares remain unliquidated")
        print(f"Final cash balance: ${cash:,.2f}")
        if not pd.isna(df['Close'].iloc[-1]):
            print(f"Estimated holding value: ${position * df['Close'].iloc[-1]:,.2f}")
        else:
            print("Cannot estimate holding value - final price is NaN")
    
    return df, trades

def calculate_performance_metrics(df, trades, initial_cash=100000):
    """Calculate comprehensive performance metrics"""
    final_value = df['Total_Value'].iloc[-1]
    total_return = ((final_value - initial_cash) / initial_cash) * 100
    
    # Calculate drawdown
    df['Peak'] = df['Total_Value'].cummax()
    df['Drawdown'] = (df['Total_Value'] - df['Peak']) / df['Peak'] * 100
    max_drawdown = df['Drawdown'].min()
    
    # Trade statistics
    profitable_trades = [t for t in trades if t['Type'] in ['Sell', 'Final Sell'] and t.get('Profit', 0) > 0]
    losing_trades = [t for t in trades if t['Type'] in ['Sell', 'Final Sell'] and t.get('Profit', 0) <= 0]
    
    win_rate = len(profitable_trades) / len([t for t in trades if t['Type'] in ['Sell', 'Final Sell']]) * 100 if len(trades) > 0 else 0
    
    # Holding periods
    holding_periods = []
    buy_date = None
    for trade in trades:
        if trade['Type'] == 'Buy':
            buy_date = trade['Date']
        elif trade['Type'] in ['Sell', 'Final Sell'] and buy_date:
            holding_periods.append((trade['Date'] - buy_date).days)
            buy_date = None
    
    avg_holding_period = np.mean(holding_periods) if holding_periods else 0
    
    return {
        'total_return': total_return,
        'final_value': final_value,
        'max_drawdown': max_drawdown,
        'num_trades': len(trades),
        'win_rate': win_rate,
        'avg_holding_period': avg_holding_period,
        'profitable_trades': len(profitable_trades),
        'losing_trades': len(losing_trades)
    }

def print_summary(ticker, df, trades, initial_cash=100000):
    """Print comprehensive backtest summary"""
    metrics = calculate_performance_metrics(df, trades, initial_cash)
    
    print(f"\n{'='*60}")
    print(f"BACKTEST SUMMARY for {ticker}")
    print(f"{'='*60}")
    print(f"Initial Cash: ${initial_cash:,.2f}")
    print(f"Final Portfolio Value: ${metrics['final_value']:,.2f}")
    print(f"Total Return: {metrics['total_return']:.2f}%")
    print(f"Maximum Drawdown: {metrics['max_drawdown']:.2f}%")
    print(f"Number of Trades: {metrics['num_trades']}")
    print(f"Win Rate: {metrics['win_rate']:.1f}%")
    print(f"Average Holding Period: {metrics['avg_holding_period']:.1f} days")
    print(f"Profitable Trades: {metrics['profitable_trades']}")
    print(f"Losing Trades: {metrics['losing_trades']}")
    
    if trades:
        sell_trades = [t for t in trades if t['Type'] in ['Sell', 'Final Sell']]
        total_profit = sum(t.get('Profit', 0) for t in sell_trades)
        print(f"Total Profit: ${total_profit:,.2f}")
        
        print(f"\nTRADE LOG:")
        print(f"{'Date':<12} {'Type':<10} {'Price':<8} {'Shares':<8} {'Profit':<10}")
        print("-" * 60)
        for trade in trades:
            profit_str = f"${trade.get('Profit', 0):.2f}" if 'Profit' in trade else ""
            print(f"{trade['Date'].strftime('%Y-%m-%d'):<12} {trade['Type']:<10} ${trade['Price']:<7.2f} {trade['Shares']:<8} {profit_str:<10}")

if __name__ == "__main__":
    ticker = "TYL"
    
    try:
        df = pd.read_csv(f"signals_{ticker}.csv", index_col=0, parse_dates=True)
        
        required_cols = ['Close', 'Buy_Signal', 'Sell_Signal']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        print(f"Running backtest for {ticker}...")
        print(f"Data range: {df.index[0].date()} to {df.index[-1].date()}")
        print(f"Total trading days: {len(df)}")
        
        df, trades = backtest_strategy(df, ticker)
        print_summary(ticker, df, trades)
        
        # Save results
        df.to_csv(f"backtest_{ticker}.csv")
        print(f"\nDetailed results saved to: backtest_{ticker}.csv")
        
    except FileNotFoundError:
        print(f"Error: Could not find signals_{ticker}.csv")
        print("Make sure you've run strategy.py first to generate the signals file.")
    except Exception as e:
        print(f"Error: {e}")
        
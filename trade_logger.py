import pandas as pd
import numpy as np
from datetime import datetime

def create_detailed_trade_log(trades, ticker, initial_cash=100000):
    """
    Create a detailed trade log with comprehensive P&L analysis
    
    Parameters:
    trades (list): List of trade dictionaries from backtest
    ticker (str): Stock ticker symbol
    initial_cash (float): Initial portfolio value
    
    Returns:
    pd.DataFrame: Detailed trade log
    """
    if not trades:
        print("No trades to log")
        return pd.DataFrame()
    
    trade_log = []
    trade_number = 0
    running_balance = initial_cash
    
    # Group trades into buy/sell pairs
    i = 0
    while i < len(trades):
        if trades[i]['Type'] == 'Buy':
            trade_number += 1
            buy_trade = trades[i]
            
            # Find corresponding sell trade
            sell_trade = None
            if i + 1 < len(trades) and trades[i + 1]['Type'] in ['Sell', 'Final Sell']:
                sell_trade = trades[i + 1]
                i += 2  # Skip both trades
            else:
                i += 1  # Only skip buy trade if no sell found
            
            if sell_trade:
                # Calculate trade metrics
                shares = buy_trade['Shares']
                buy_price = buy_trade['Price']
                sell_price = sell_trade['Price']
                buy_date = buy_trade['Date']
                sell_date = sell_trade['Date']
                
                # Calculate P&L
                gross_profit = sell_trade.get('Profit', (shares * sell_price) - (shares * buy_price))
                gross_profit_pct = (gross_profit / (shares * buy_price)) * 100 if shares * buy_price > 0 else 0
                
                # Calculate holding period
                holding_days = (sell_date - buy_date).days
                
                # Update running balance
                running_balance += gross_profit
                
                # Determine if trade was profitable
                trade_result = "Win" if gross_profit > 0 else "Loss" if gross_profit < 0 else "Break-even"
                
                trade_entry = {
                    'Trade_Number': trade_number,
                    'Ticker': ticker,
                    'Entry_Date': buy_date.strftime('%Y-%m-%d'),
                    'Entry_Price': round(buy_price, 2),
                    'Exit_Date': sell_date.strftime('%Y-%m-%d'),
                    'Exit_Price': round(sell_price, 2),
                    'Shares': shares,
                    'Position_Size': round(shares * buy_price, 2),
                    'Gross_Profit': round(gross_profit, 2),
                    'Profit_Percent': round(gross_profit_pct, 2),
                    'Holding_Days': holding_days,
                    'Trade_Result': trade_result,
                    'Running_Balance': round(running_balance, 2),
                    'Trade_Type': sell_trade['Type']
                }
                
                trade_log.append(trade_entry)
        else:
            i += 1
    
    return pd.DataFrame(trade_log)

def generate_trade_summary_stats(trade_df):
    """
    Generate comprehensive trade summary statistics
    
    Parameters:
    trade_df (pd.DataFrame): Trade log dataframe
    
    Returns:
    dict: Summary statistics
    """
    if trade_df.empty:
        return {}
    
    total_trades = len(trade_df)
    winning_trades = len(trade_df[trade_df['Gross_Profit'] > 0])
    losing_trades = len(trade_df[trade_df['Gross_Profit'] < 0])
    breakeven_trades = len(trade_df[trade_df['Gross_Profit'] == 0])
    
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    total_profit = trade_df['Gross_Profit'].sum()
    avg_profit = trade_df['Gross_Profit'].mean()
    
    # Winning trade stats
    winning_df = trade_df[trade_df['Gross_Profit'] > 0]
    avg_win = winning_df['Gross_Profit'].mean() if len(winning_df) > 0 else 0
    largest_win = winning_df['Gross_Profit'].max() if len(winning_df) > 0 else 0
    
    # Losing trade stats
    losing_df = trade_df[trade_df['Gross_Profit'] < 0]
    avg_loss = losing_df['Gross_Profit'].mean() if len(losing_df) > 0 else 0
    largest_loss = losing_df['Gross_Profit'].min() if len(losing_df) > 0 else 0
    
    # Profit factor (gross wins / gross losses)
    gross_wins = winning_df['Gross_Profit'].sum() if len(winning_df) > 0 else 0
    gross_losses = abs(losing_df['Gross_Profit'].sum()) if len(losing_df) > 0 else 0
    profit_factor = gross_wins / gross_losses if gross_losses > 0 else float('inf') if gross_wins > 0 else 0
    
    # Holding period stats
    avg_holding_days = trade_df['Holding_Days'].mean()
    min_holding_days = trade_df['Holding_Days'].min()
    max_holding_days = trade_df['Holding_Days'].max()
    
    # Return stats
    avg_return_pct = trade_df['Profit_Percent'].mean()
    best_return_pct = trade_df['Profit_Percent'].max()
    worst_return_pct = trade_df['Profit_Percent'].min()
    
    return {
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'breakeven_trades': breakeven_trades,
        'win_rate': round(win_rate, 2),
        'total_profit': round(total_profit, 2),
        'avg_profit_per_trade': round(avg_profit, 2),
        'avg_win': round(avg_win, 2),
        'avg_loss': round(avg_loss, 2),
        'largest_win': round(largest_win, 2),
        'largest_loss': round(largest_loss, 2),
        'profit_factor': round(profit_factor, 2),
        'gross_wins': round(gross_wins, 2),
        'gross_losses': round(gross_losses, 2),
        'avg_holding_days': round(avg_holding_days, 1),
        'min_holding_days': min_holding_days,
        'max_holding_days': max_holding_days,
        'avg_return_percent': round(avg_return_pct, 2),
        'best_return_percent': round(best_return_pct, 2),
        'worst_return_percent': round(worst_return_pct, 2)
    }

def print_trade_analysis(trade_df, stats, ticker):
    """
    Print comprehensive trade analysis to console
    """
    print(f"\n{'='*80}")
    print(f"DETAILED TRADE ANALYSIS FOR {ticker}")
    print(f"{'='*80}")
    
    if trade_df.empty:
        print("No completed trades found.")
        return
    
    # Overall Performance
    print(f"\nOVERALL PERFORMANCE:")
    print(f"{'─'*50}")
    print(f"Total Trades: {stats['total_trades']}")
    print(f"Winning Trades: {stats['winning_trades']} ({stats['win_rate']:.1f}%)")
    print(f"Losing Trades: {stats['losing_trades']}")
    print(f"Break-even Trades: {stats['breakeven_trades']}")
    print(f"Total P&L: ${stats['total_profit']:,.2f}")
    print(f"Average P&L per Trade: ${stats['avg_profit_per_trade']:,.2f}")
    print(f"Profit Factor: {stats['profit_factor']:.2f}")
    
    # Trade Details
    print(f"\nPROFIT/LOSS BREAKDOWN:")
    print(f"{'─'*50}")
    print(f"Gross Profits: ${stats['gross_wins']:,.2f}")
    print(f"Gross Losses: ${stats['gross_losses']:,.2f}")
    print(f"Average Win: ${stats['avg_win']:,.2f}")
    print(f"Average Loss: ${stats['avg_loss']:,.2f}")
    print(f"Largest Win: ${stats['largest_win']:,.2f}")
    print(f"Largest Loss: ${stats['largest_loss']:,.2f}")
    
    # Return Analysis
    print(f"\nRETURN ANALYSIS:")
    print(f"{'─'*50}")
    print(f"Average Return per Trade: {stats['avg_return_percent']:.2f}%")
    print(f"Best Trade Return: {stats['best_return_percent']:.2f}%")
    print(f"Worst Trade Return: {stats['worst_return_percent']:.2f}%")
    
    # Holding Period Analysis
    print(f"\nHOLDING PERIOD ANALYSIS:")
    print(f"{'─'*50}")
    print(f"Average Holding Period: {stats['avg_holding_days']:.1f} days")
    print(f"Shortest Hold: {stats['min_holding_days']} days")
    print(f"Longest Hold: {stats['max_holding_days']} days")
    
    # Recent Trades Summary
    print(f"\nRECENT TRADES (Last 5):")
    print(f"{'─'*50}")
    recent_trades = trade_df.tail(5)
    
    for _, trade in recent_trades.iterrows():
        result_emoji = "✅" if trade['Gross_Profit'] > 0 else "❌" if trade['Gross_Profit'] < 0 else "➖"
        print(f"{result_emoji} Trade #{trade['Trade_Number']:2d}: {trade['Entry_Date']} → {trade['Exit_Date']} "
              f"({trade['Holding_Days']:2d} days) | "
              f"${trade['Entry_Price']:6.2f} → ${trade['Exit_Price']:6.2f} | "
              f"P&L: ${trade['Gross_Profit']:8.2f} ({trade['Profit_Percent']:+6.2f}%)")
    
    # Top Winners and Losers
    if len(trade_df) > 1:
        print(f"\nTOP 3 WINNERS:")
        print(f"{'─'*50}")
        top_winners = trade_df.nlargest(3, 'Gross_Profit')
        for _, trade in top_winners.iterrows():
            print(f"Trade #{trade['Trade_Number']:2d}: {trade['Entry_Date']} | "
                  f"P&L: ${trade['Gross_Profit']:8.2f} ({trade['Profit_Percent']:+6.2f}%)")
        
        print(f"\nTOP 3 LOSERS:")
        print(f"{'─'*50}")
        top_losers = trade_df.nsmallest(3, 'Gross_Profit')
        for _, trade in top_losers.iterrows():
            print(f"Trade #{trade['Trade_Number']:2d}: {trade['Entry_Date']} | "
                  f"P&L: ${trade['Gross_Profit']:8.2f} ({trade['Profit_Percent']:+6.2f}%)")

def export_trade_log(trade_df, stats, ticker, export_format='both'):
    """
    Export trade log and summary to files
    
    Parameters:
    trade_df (pd.DataFrame): Trade log dataframe
    stats (dict): Summary statistics
    ticker (str): Stock ticker
    export_format (str): 'csv', 'excel', or 'both'
    """
    if trade_df.empty:
        print("No trades to export.")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Export detailed trade log
    if export_format in ['csv', 'both']:
        trade_filename = f"trade_log_{ticker}_{timestamp}.csv"
        trade_df.to_csv(trade_filename, index=False)
        print(f"Detailed trade log exported: {trade_filename}")
    
    if export_format in ['excel', 'both']:
        excel_filename = f"trade_analysis_{ticker}_{timestamp}.xlsx"
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            # Trade log sheet
            trade_df.to_excel(writer, sheet_name='Trade_Log', index=False)
            
            # Summary stats sheet
            stats_df = pd.DataFrame(list(stats.items()), columns=['Metric', 'Value'])
            stats_df.to_excel(writer, sheet_name='Summary_Stats', index=False)
            
            # Monthly performance
            if 'Entry_Date' in trade_df.columns:
                trade_df['Entry_Month'] = pd.to_datetime(trade_df['Entry_Date']).dt.to_period('M')
                monthly_perf = trade_df.groupby('Entry_Month').agg({
                    'Gross_Profit': ['sum', 'count', 'mean'],
                    'Profit_Percent': 'mean'
                }).round(2)
                monthly_perf.columns = ['Total_Profit', 'Trade_Count', 'Avg_Profit', 'Avg_Return_Pct']
                monthly_perf.to_excel(writer, sheet_name='Monthly_Performance')
        
        print(f"✅ Excel trade analysis exported: {excel_filename}")
    
    # Export summary statistics as text file
    summary_filename = f"trade_summary_{ticker}_{timestamp}.txt"
    with open(summary_filename, 'w') as f:
        f.write(f"TRADE SUMMARY FOR {ticker}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*60 + "\n\n")
        
        f.write("PERFORMANCE METRICS:\n")
        f.write("-" * 30 + "\n")
        for key, value in stats.items():
            formatted_key = key.replace('_', ' ').title()
            if isinstance(value, float):
                if 'percent' in key.lower() or 'rate' in key.lower():
                    f.write(f"{formatted_key}: {value:.2f}%\n")
                elif 'factor' in key.lower():
                    f.write(f"{formatted_key}: {value:.2f}\n")
                else:
                    f.write(f"{formatted_key}: ${value:,.2f}\n")
            else:
                f.write(f"{formatted_key}: {value}\n")
    
    print(f"✅ Summary report exported: {summary_filename}")

def run_complete_trade_analysis(ticker, initial_cash=100000):
    """
    Run complete trade analysis for a given ticker
    This function integrates with your existing backtest results
    """
    try:
        # Load backtest results (assumes you've run backtest.py)
        backtest_file = f"backtest_{ticker}.csv"
        df = pd.read_csv(backtest_file, index_col=0, parse_dates=True)
        print(f"Loaded backtest data for {ticker}")
        
        # Re-run backtest to get trades (you could also save/load trades separately)
        from backtest import backtest_strategy
        signals_file = f"signals_{ticker}.csv"
        signals_df = pd.read_csv(signals_file, index_col=0, parse_dates=True)
        
        # Run backtest to get trades
        _, trades = backtest_strategy(signals_df, ticker, initial_cash)
        
        if not trades:
            print(f"No trades found for {ticker}")
            return None, None
        
        print(f"Found {len(trades)} trade entries for {ticker}")
        
        # Create detailed trade log
        trade_df = create_detailed_trade_log(trades, ticker, initial_cash)
        
        # Generate summary statistics
        stats = generate_trade_summary_stats(trade_df)
        
        # Print analysis to console
        print_trade_analysis(trade_df, stats, ticker)
        
        # Export to files
        export_trade_log(trade_df, stats, ticker, export_format='both')
        
        return trade_df, stats
        
    except FileNotFoundError as e:
        print(f"Error: Required files not found for {ticker}")
        print("Make sure you've run the complete pipeline:")
        print("1. data_loader.py")
        print("2. strategy.py") 
        print("3. backtest.py")
        return None, None
    except Exception as e:
        print(f"Error processing {ticker}: {e}")
        return None, None

if __name__ == "__main__":
    test_tickers = ['TYL', 'TSCO', 'MPWR']
    
    print("🚀 Starting comprehensive trade log analysis...")
    print("="*60)
    
    all_results = {}
    
    for ticker in test_tickers:
        print(f"\n{'='*60}")
        print(f"PROCESSING {ticker}")
        print(f"{'='*60}")
        
        trade_df, stats = run_complete_trade_analysis(ticker)
        
        if trade_df is not None and stats is not None:
            all_results[ticker] = {
                'trade_log': trade_df,
                'stats': stats
            }
            print(f"✅ Successfully processed {ticker}")
        else:
            print(f"❌ Failed to process {ticker}")
    
    # Create combined summary if multiple tickers processed
    if len(all_results) > 1:
        print(f"\n{'='*60}")
        print("MULTI-TICKER COMPARISON")
        print(f"{'='*60}")
        
        comparison_data = []
        for ticker, results in all_results.items():
            stats = results['stats']
            comparison_data.append({
                'Ticker': ticker,
                'Total_Trades': stats['total_trades'],
                'Win_Rate_%': stats['win_rate'],
                'Total_Profit': stats['total_profit'],
                'Avg_Profit_Per_Trade': stats['avg_profit_per_trade'],
                'Profit_Factor': stats['profit_factor'],
                'Avg_Return_%': stats['avg_return_percent'],
                'Avg_Holding_Days': stats['avg_holding_days']
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        comparison_df = comparison_df.sort_values('Total_Profit', ascending=False)
        
        print("\nPERFORMANCE COMPARISON:")
        print(comparison_df.to_string(index=False, float_format='%.2f'))
        
        # Export comparison
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        comparison_df.to_csv(f"trade_comparison_{timestamp}.csv", index=False)
        print(f"\n✅ Comparison exported: trade_comparison_{timestamp}.csv")
    
    print(f"\nTrade log analysis complete!")
    print(f"📁 Check your directory for exported files:")
    print("   - trade_log_[TICKER]_[TIMESTAMP].csv")
    print("   - trade_analysis_[TICKER]_[TIMESTAMP].xlsx") 
    print("   - trade_summary_[TICKER]_[TIMESTAMP].txt")
    if len(all_results) > 1:
        print("   - trade_comparison_[TIMESTAMP].csv")
        
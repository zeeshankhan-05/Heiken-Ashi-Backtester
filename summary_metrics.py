import pandas as pd
import numpy as np
import json
from datetime import datetime
from data_loader import fetch_all, process_ticker_data
from strategy import generate_signals
from backtest import backtest_strategy, calculate_performance_metrics

def generate_comprehensive_summary(tickers=None):
    """
    Uses your existing pipeline to generate summary metrics for multiple stocks
    """
    if tickers is None:
        tickers = ['MPWR', 'TSCO', 'TYL']
    
    all_results = {}
    summary_data = []
    
    print(f"Running comprehensive backtest for {len(tickers)} tickers...")
    
    for ticker in tickers:
        print(f"\n{'='*50}")
        print(f"Processing {ticker}")
        print(f"{'='*50}")
        
        try:
            # Step 1: Check if processed data exists, if not create it
            filename = f"indicators_{ticker}.csv"
            try:
                df = pd.read_csv(filename, index_col=0, parse_dates=True)
                print(f"Loaded existing data from {filename}")
            except FileNotFoundError:
                print(f"Data file not found for {ticker}, fetching new data...")
                # Use your existing data_loader functions
                from data_loader import fetch_stock_data, process_ticker_data
                raw_df = fetch_stock_data(ticker)
                df = process_ticker_data(ticker, raw_df)
                df.to_csv(filename)
                print(f"Saved new data to {filename}")
            
            # Step 2: Generate signals using your existing strategy
            df_with_signals = generate_signals(df)
            signals_filename = f"signals_{ticker}.csv"
            df_with_signals.to_csv(signals_filename)
            
            # Step 3: Run backtest using your existing backtest function
            df_backtest, trades = backtest_strategy(df_with_signals, ticker)
            
            # Step 4: Calculate metrics using your existing function
            metrics = calculate_performance_metrics(df_backtest, trades)
            
            # Step 5: Add additional metrics
            enhanced_metrics = enhance_metrics(df_backtest, trades, metrics, ticker)
            
            # Store results
            all_results[ticker] = {
                'ticker': ticker,
                'metrics': enhanced_metrics,
                'trades': trades,
                'data_start': df.index[0].strftime('%Y-%m-%d'),
                'data_end': df.index[-1].strftime('%Y-%m-%d'),
                'total_days': len(df)
            }
            
            # Add to summary data
            summary_data.append({
                'Ticker': ticker,
                'Total_Return_%': enhanced_metrics['total_return'],
                'Final_Value': enhanced_metrics['final_value'],
                'Total_Profit': enhanced_metrics.get('total_profit', 0),
                'Max_Drawdown_%': enhanced_metrics['max_drawdown'],
                'Num_Trades': enhanced_metrics['num_trades'],
                'Win_Rate_%': enhanced_metrics['win_rate'],
                'Avg_Holding_Days': enhanced_metrics['avg_holding_period'],
                'Profitable_Trades': enhanced_metrics['profitable_trades'],
                'Losing_Trades': enhanced_metrics['losing_trades'],
                'Period_Years': enhanced_metrics.get('period_years', 0)
            })
            
            # Print individual summary
            print_individual_summary(ticker, enhanced_metrics, trades)
            
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue
    
    # Generate final summary
    if summary_data:
        save_summary_results(summary_data, all_results)
    
    return all_results

def enhance_metrics(df, trades, existing_metrics, ticker):
    """
Enhance your existing metrics with additional calculations
    """
    enhanced = existing_metrics.copy()
    
    # Calculate total profit from trades
    sell_trades = [t for t in trades if t['Type'] in ['Sell', 'Final Sell']]
    total_profit = sum(t.get('Profit', 0) for t in sell_trades)
    enhanced['total_profit'] = round(total_profit, 2)
    
    # Calculate period in years
    if len(df) > 0:
        years = (df.index[-1] - df.index[0]).days / 365.25
        enhanced['period_years'] = round(years, 1)
        
        # Calculate annualized return
        if years > 0 and 'final_value' in enhanced:
            initial_value = 100000  # Your initial cash
            annualized_return = ((enhanced['final_value'] / initial_value) ** (1/years) - 1) * 100
            enhanced['annualized_return'] = round(annualized_return, 2)
    
    # Add average profit per trade
    if sell_trades:
        enhanced['avg_profit_per_trade'] = round(total_profit / len(sell_trades), 2)
    else:
        enhanced['avg_profit_per_trade'] = 0.0
    
    return enhanced

def print_individual_summary(ticker, metrics, trades):
    """Print summary for individual ticker"""
    print(f"\nSUMMARY for {ticker}:")
    print(f"Total Return: {metrics['total_return']:.2f}%")
    if 'annualized_return' in metrics:
        print(f"Annualized Return: {metrics['annualized_return']:.2f}%")
    print(f"Final Value: ${metrics['final_value']:,.2f}")
    print(f"Total Profit: ${metrics.get('total_profit', 0):,.2f}")
    print(f"Max Drawdown: {metrics['max_drawdown']:.2f}%")
    print(f"Number of Trades: {metrics['num_trades']}")
    print(f"Win Rate: {metrics['win_rate']:.1f}%")
    print(f"Avg Holding Period: {metrics['avg_holding_period']:.1f} days")
    
    if trades:
        print(f"\nRecent Trades:")
        for trade in trades[-3:]:  # Last 3 trades
            profit_str = f" (Profit: ${trade.get('Profit', 0):.2f})" if 'Profit' in trade else ""
            print(f"  {trade['Date'].strftime('%Y-%m-%d')}: {trade['Type']} {trade['Shares']} shares @ ${trade['Price']:.2f}{profit_str}")

def save_summary_results(summary_data, all_results):
    """Save summary results to files"""
    summary_df = pd.DataFrame(summary_data)
    summary_df = summary_df.sort_values('Total_Return_%', ascending=False)
    
    # Save summary CSV
    summary_df.to_csv('backtest_summary.csv', index=False)
    print(f"\nSaved summary to: backtest_summary.csv")
    
    # Save detailed JSON results
    serializable_results = {}
    for ticker, result in all_results.items():
        trades_serializable = []
        for trade in result['trades']:
            trade_copy = trade.copy()
            if hasattr(trade['Date'], 'strftime'):
                trade_copy['Date'] = trade['Date'].strftime('%Y-%m-%d')
            trades_serializable.append(trade_copy)
        
        serializable_results[ticker] = {
            'ticker': result['ticker'],
            'metrics': result['metrics'],
            'trades': trades_serializable,
            'data_start': result['data_start'],
            'data_end': result['data_end'],
            'total_days': result['total_days']
        }
    
    with open('backtest_detailed_results.json', 'w') as f:
        json.dump(serializable_results, f, indent=2, default=str)
    print(f"Saved detailed results to: backtest_detailed_results.json")
    
    # Print overall summary
    print(f"\n{'='*80}")
    print("OVERALL BACKTEST SUMMARY")
    print(f"{'='*80}")
    print(f"Tested {len(all_results)} stocks")
    
    if len(summary_df) > 0:
        print(f"\nTop Performers by Total Return:")
        print(summary_df[['Ticker', 'Total_Return_%', 'Win_Rate_%', 'Num_Trades']].head())
        
        print(f"\nPortfolio Statistics:")
        print(f"Average Return: {summary_df['Total_Return_%'].mean():.2f}%")
        print(f"Best Performer: {summary_df.iloc[0]['Ticker']} ({summary_df.iloc[0]['Total_Return_%']:.2f}%)")
        print(f"Worst Performer: {summary_df.iloc[-1]['Ticker']} ({summary_df.iloc[-1]['Total_Return_%']:.2f}%)")
        print(f"Average Win Rate: {summary_df['Win_Rate_%'].mean():.1f}%")
        print(f"Total Trades Across All Stocks: {summary_df['Num_Trades'].sum()}")

if __name__ == "__main__":
    tickers_to_test = ['MPWR', 'TSCO', 'TYL']
    
    print("Starting comprehensive backtest using existing pipeline...")
    results = generate_comprehensive_summary(tickers_to_test)
    
    print(f"\nBacktesting complete!")
    print(f"Generated files:")
    print(f"- backtest_summary.csv")
    print(f"- backtest_detailed_results.json")
    print(f"- Individual signals_[TICKER].csv files")
    
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np

def create_backtest_visualizations(ticker, save_plots=True):
    """
    Create comprehensive visualizations for backtest results:
    1. Cumulative returns over time
    2. Stock price with buy/sell arrows
    3. Drawdown chart
    4. Combined dashboard
    """
    
    try:
        # Load the backtest results
        backtest_file = f"backtest_{ticker}.csv"
        df = pd.read_csv(backtest_file, index_col=0, parse_dates=True)
        print(f"Loaded backtest data for {ticker}: {len(df)} rows")
        
        # Load the signals data for trade markers
        signals_file = f"signals_{ticker}.csv"
        signals_df = pd.read_csv(signals_file, index_col=0, parse_dates=True)
        
    except FileNotFoundError as e:
        print(f"Error: Could not find required files for {ticker}")
        print(f"Make sure you have run the full pipeline first:")
        print(f"1. data_loader.py")
        print(f"2. strategy.py") 
        print(f"3. backtest.py")
        return
    
    # Calculate additional metrics for visualization
    initial_cash = 100000
    df['Returns'] = (df['Total_Value'] / initial_cash - 1) * 100
    df['Peak'] = df['Total_Value'].cummax()
    df['Drawdown'] = (df['Total_Value'] - df['Peak']) / df['Peak'] * 100
    
    # Create the visualizations
    fig = plt.figure(figsize=(20, 16))
    
    # 1. Cumulative Returns Chart
    ax1 = plt.subplot(2, 2, 1)
    ax1.plot(df.index, df['Returns'], color='navy', linewidth=2, label='Portfolio Returns')
    ax1.axhline(y=0, color='red', linestyle='--', alpha=0.7, label='Break-even')
    ax1.set_title(f'{ticker} - Cumulative Returns Over Time', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Cumulative Return (%)')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Format dates on x-axis
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    
    # Add performance text
    final_return = df['Returns'].iloc[-1]
    max_return = df['Returns'].max()
    min_return = df['Returns'].min()
    ax1.text(0.02, 0.95, f'Final Return: {final_return:.1f}%\nMax Return: {max_return:.1f}%\nMin Return: {min_return:.1f}%', 
             transform=ax1.transAxes, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    # 2. Stock Price with Buy/Sell Arrows
    ax2 = plt.subplot(2, 2, 2)
    ax2.plot(df.index, df['Close'], color='black', linewidth=1.5, label='Stock Price', alpha=0.8)
    
    # Add buy signals (green arrows up)
    buy_signals = signals_df[signals_df['Buy_Signal'] == True]
    if len(buy_signals) > 0:
        ax2.scatter(buy_signals.index, buy_signals['Close'], 
                   marker='^', color='green', s=100, label='Buy Signal', zorder=5)
    
    # Add sell signals (red arrows down)
    sell_signals = signals_df[signals_df['Sell_Signal'] == True]
    if len(sell_signals) > 0:
        ax2.scatter(sell_signals.index, sell_signals['Close'], 
                   marker='v', color='red', s=100, label='Sell Signal', zorder=5)
    
    ax2.set_title(f'{ticker} - Stock Price with Trading Signals', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Price ($)')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # Format dates
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
    
    # Add price statistics
    price_stats = f'Price Range: ${df["Close"].min():.2f} - ${df["Close"].max():.2f}\nCurrent: ${df["Close"].iloc[-1]:.2f}'
    ax2.text(0.02, 0.95, price_stats, transform=ax2.transAxes, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    # 3. Drawdown Chart
    ax3 = plt.subplot(2, 2, 3)
    ax3.fill_between(df.index, df['Drawdown'], 0, color='red', alpha=0.3, label='Drawdown')
    ax3.plot(df.index, df['Drawdown'], color='darkred', linewidth=1)
    ax3.set_title(f'{ticker} - Portfolio Drawdown', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Date')
    ax3.set_ylabel('Drawdown (%)')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # Format dates
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax3.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
    
    # Add drawdown statistics
    max_drawdown = df['Drawdown'].min()
    avg_drawdown = df['Drawdown'].mean()
    ax3.text(0.02, 0.05, f'Max Drawdown: {max_drawdown:.1f}%\nAvg Drawdown: {avg_drawdown:.1f}%', 
             transform=ax3.transAxes, verticalalignment='bottom',
             bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.8))
    
    # 4. Portfolio Value Over Time
    ax4 = plt.subplot(2, 2, 4)
    ax4.plot(df.index, df['Total_Value'], color='purple', linewidth=2, label='Portfolio Value')
    ax4.plot(df.index, df['Cash'], color='green', linewidth=1, alpha=0.7, label='Cash')
    ax4.plot(df.index, df['Holdings'], color='orange', linewidth=1, alpha=0.7, label='Holdings Value')
    ax4.axhline(y=initial_cash, color='gray', linestyle='--', alpha=0.7, label='Initial Value')
    
    ax4.set_title(f'{ticker} - Portfolio Composition Over Time', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Date')
    ax4.set_ylabel('Value ($)')
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    # Format dates
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax4.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)
    
    # Add final values
    final_value = df['Total_Value'].iloc[-1]
    final_cash = df['Cash'].iloc[-1]
    final_holdings = df['Holdings'].iloc[-1]
    ax4.text(0.02, 0.95, f'Final Portfolio: ${final_value:,.0f}\nCash: ${final_cash:,.0f}\nHoldings: ${final_holdings:,.0f}', 
             transform=ax4.transAxes, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
    
    plt.tight_layout(pad=3.0)
    
    if save_plots:
        filename = f'backtest_visualization_{ticker}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Saved comprehensive visualization: {filename}")
    
    plt.show()
    
    # Create individual focused charts
    create_individual_charts(ticker, df, signals_df, save_plots)

def create_individual_charts(ticker, df, signals_df, save_plots=True):
    """Create individual focused charts for detailed analysis"""
    
    # 1. Detailed Price Chart with Signals
    plt.figure(figsize=(15, 8))
    plt.plot(df.index, df['Close'], color='black', linewidth=2, label='Stock Price')
    
    # Add buy/sell signals
    buy_signals = signals_df[signals_df['Buy_Signal'] == True]
    sell_signals = signals_df[signals_df['Sell_Signal'] == True]
    
    if len(buy_signals) > 0:
        plt.scatter(buy_signals.index, buy_signals['Close'], 
                   marker='^', color='green', s=150, label=f'Buy Signals ({len(buy_signals)})', 
                   zorder=5, edgecolor='darkgreen', linewidth=1)
    
    if len(sell_signals) > 0:
        plt.scatter(sell_signals.index, sell_signals['Close'], 
                   marker='v', color='red', s=150, label=f'Sell Signals ({len(sell_signals)})', 
                   zorder=5, edgecolor='darkred', linewidth=1)
    
    plt.title(f'{ticker} Stock Price with Trading Signals', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Price ($)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=12)
    
    # Format dates
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    if save_plots:
        plt.savefig(f'price_signals_{ticker}.png', dpi=300, bbox_inches='tight')
        print(f"Saved detailed price chart: price_signals_{ticker}.png")
    plt.show()
    
    # 2. Returns vs Drawdown Comparison
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), sharex=True)
    
    # Returns
    ax1.plot(df.index, df['Returns'], color='blue', linewidth=2)
    ax1.axhline(y=0, color='red', linestyle='--', alpha=0.7)
    ax1.set_title(f'{ticker} - Cumulative Returns', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Returns (%)')
    ax1.grid(True, alpha=0.3)
    
    # Drawdown
    ax2.fill_between(df.index, df['Drawdown'], 0, color='red', alpha=0.4)
    ax2.plot(df.index, df['Drawdown'], color='darkred', linewidth=1)
    ax2.set_title(f'{ticker} - Portfolio Drawdown', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Drawdown (%)')
    ax2.grid(True, alpha=0.3)
    
    # Format dates
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    if save_plots:
        plt.savefig(f'returns_drawdown_{ticker}.png', dpi=300, bbox_inches='tight')
        print(f"Saved returns/drawdown chart: returns_drawdown_{ticker}.png")
    plt.show()

def create_multi_ticker_comparison(tickers=None):
    """Create comparison charts for multiple tickers"""
    if tickers is None:
        tickers = ['MPWR', 'TSCO', 'TYL']
    
    fig, axes = plt.subplots(2, 2, figsize=(20, 12))
    
    colors = ['blue', 'red', 'green', 'purple', 'orange']
    
    for i, ticker in enumerate(tickers):
        try:
            df = pd.read_csv(f"backtest_{ticker}.csv", index_col=0, parse_dates=True)
            initial_cash = 100000
            df['Returns'] = (df['Total_Value'] / initial_cash - 1) * 100
            df['Drawdown'] = (df['Total_Value'] - df['Total_Value'].cummax()) / df['Total_Value'].cummax() * 100
            
            color = colors[i % len(colors)]
            
            # Returns comparison
            axes[0, 0].plot(df.index, df['Returns'], color=color, linewidth=2, label=ticker)
            
            # Drawdown comparison
            axes[0, 1].plot(df.index, df['Drawdown'], color=color, linewidth=2, label=ticker)
            
            # Portfolio value comparison
            axes[1, 0].plot(df.index, df['Total_Value'], color=color, linewidth=2, label=ticker)
            
            # Price comparison (normalized to start at 100)
            price_normalized = (df['Close'] / df['Close'].iloc[0]) * 100
            axes[1, 1].plot(df.index, price_normalized, color=color, linewidth=2, label=ticker)
            
        except FileNotFoundError:
            print(f"Warning: Could not load data for {ticker}")
            continue
    
    # Configure subplots
    axes[0, 0].set_title('Cumulative Returns Comparison', fontsize=14, fontweight='bold')
    axes[0, 0].set_ylabel('Returns (%)')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].legend()
    axes[0, 0].axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    axes[0, 1].set_title('Drawdown Comparison', fontsize=14, fontweight='bold')
    axes[0, 1].set_ylabel('Drawdown (%)')
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].legend()
    
    axes[1, 0].set_title('Portfolio Value Comparison', fontsize=14, fontweight='bold')
    axes[1, 0].set_ylabel('Portfolio Value ($)')
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].legend()
    axes[1, 0].axhline(y=100000, color='black', linestyle='--', alpha=0.5, label='Initial')
    
    axes[1, 1].set_title('Stock Price Comparison (Normalized)', fontsize=14, fontweight='bold')
    axes[1, 1].set_ylabel('Normalized Price (Base=100)')
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].legend()
    axes[1, 1].axhline(y=100, color='black', linestyle='--', alpha=0.5, label='Starting Point')
    
    # Format dates for bottom row
    for ax in [axes[1, 0], axes[1, 1]]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    plt.savefig('multi_ticker_comparison.png', dpi=300, bbox_inches='tight')
    print("Saved multi-ticker comparison: multi_ticker_comparison.png")
    plt.show()

def print_visualization_summary(ticker):
    """Print a summary of what visualizations were created"""
    print(f"\n{'='*60}")
    print(f"VISUALIZATION SUMMARY for {ticker}")
    print(f"{'='*60}")
    print("Created the following charts:")
    print("1. Comprehensive Dashboard (4-panel view):")
    print("   - Cumulative returns over time")
    print("   - Stock price with buy/sell arrows")  
    print("   - Portfolio drawdown chart")
    print("   - Portfolio composition over time")
    print("2. Detailed Price Chart with Trading Signals")
    print("3. Returns vs Drawdown Comparison")
    print("\nFiles saved:")
    print(f"- backtest_visualization_{ticker}.png")
    print(f"- price_signals_{ticker}.png") 
    print(f"- returns_drawdown_{ticker}.png")

if __name__ == "__main__":
    test_tickers = ['TYL', 'TSCO', 'MPWR']
    
    print("Creating backtest visualizations...")
    print("Make sure you have run the complete pipeline first:")
    print("1. data_loader.py")
    print("2. strategy.py")
    print("3. backtest.py")
    print()
    
    for ticker in test_tickers:
        print(f"\n{'='*50}")
        print(f"Creating visualizations for {ticker}")
        print(f"{'='*50}")
        
        try:
            create_backtest_visualizations(ticker)
            print_visualization_summary(ticker)
        except Exception as e:
            print(f"Error creating visualizations for {ticker}: {e}")
            continue
    
    # Create comparison chart if multiple tickers processed
    print(f"\n{'='*50}")
    print("Creating multi-ticker comparison...")
    print(f"{'='*50}")
    try:
        create_multi_ticker_comparison(test_tickers)
        print("Multi-ticker comparison chart created successfully!")
    except Exception as e:
        print(f"Error creating comparison chart: {e}")
    
    print(f"\nVisualization process complete!")
    print("Check the generated PNG files for your charts.")

import pandas as pd

# Adds Buy and Sell signal columns to the DataFrame
def generate_signals(df):
    df = df.copy()
    
    # Ensure required columns exist
    if 'Current_Holding' not in df.columns:
        df['Current_Holding'] = 0

    df['Buy_Signal'] = False
    df['Sell_Signal'] = False

    cash_limit = 10000

    for i in range(1, len(df)):
        date = df.index[i]
        weekday = date.weekday()  # Monday=0, Friday=4

        # SELL RULES
        # Rule 1: Close < HA_100_MA
        rule1 = df['HA_Close'].iloc[i] < df['HA_100_MA'].iloc[i]

        # Rule 2: HA_50_MA not increasing
        prev_ma = df['HA_50_MA'].iloc[i - 1]
        curr_ma = df['HA_50_MA'].iloc[i]
        rule2 = curr_ma <= prev_ma

        # Rule 3: MACD Histogram is negative or decreasing
        macd_hist_today = df['MACD_Hist'].iloc[i]
        macd_hist_yesterday = df['MACD_Hist'].iloc[i - 1]
        rule3 = (macd_hist_today < 0) or (macd_hist_today < macd_hist_yesterday)

        if rule1 and rule2 and rule3:
            df.loc[date, 'Sell_Signal'] = True
            print(f"[SELL] {date.date()} — Close < HA_100_MA, HA_50_MA not rising, MACD weakening")

        # BUY RULES
        is_buy_day = weekday in [0, 2, 4]
        under_limit = df['Current_Holding'].iloc[i] < cash_limit
        not_sell_day = not df['Sell_Signal'].iloc[i]

        if is_buy_day and under_limit and not_sell_day:
            df.loc[date, 'Buy_Signal'] = True

    return df

# Main Testing
if __name__ == "__main__":
    # Update the csv file name for the ticker wanting to test
    df = pd.read_csv("indicators_TSCO.csv", index_col=0, parse_dates=True)
    df = generate_signals(df)

    print(df[['HA_50_MA', 'HA_100_MA', 'MACD_Hist', 'Buy_Signal', 'Sell_Signal']].tail(10))
    df.to_csv("signals_TSCO.csv")
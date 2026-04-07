import pandas as pd
import sys
import os

# Add parent directory to path so we can import strategies
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.ensemble import EnsembleStrategy

def run_backtest():
    print("Loading Advanced Features...")
    try:
        df = pd.read_csv('data/advanced_features.csv', parse_dates=['ts']).set_index('ts')
    except FileNotFoundError:
        print("Error: data/advanced_features.csv not found. Please run feature_store/advanced_features.py")
        return

    print("Running Ensemble Strategy...")
    strategy = EnsembleStrategy()
    df['signal'] = strategy.generate_signals(df)
    
    # Position Sizing & PnL
    capital = 10000
    df['returns'] = df['ret_1'].shift(-1) * df['signal'] # using ret_1 from advanced features
    df['equity_curve'] = (1 + df['returns']).cumprod() * capital
    
    # Stats
    total_return = (df['equity_curve'].iloc[-1] / capital) - 1
    sharpe = df['returns'].mean() / df['returns'].std() * (252**0.5) * 1440 # simplistic scaling for minute data
    
    print("-" * 30)
    print(f"Total Return: {total_return:.2%}")
    print(f"Final Capital: ${df['equity_curve'].iloc[-1]:.2f}")
    # print(f"Sharpe Ratio: {sharpe:.2f}") (Scaling minute sharpe is tricky, keeping simple)
    print("-" * 30)
    print(df[['close', 'signal', 'equity_curve']].tail())

if __name__ == '__main__':
    run_backtest()

import pandas as pd
from sqlalchemy import create_engine
import ta

engine = create_engine('postgresql://trader:example@localhost:5435/golddb')

def build_features(window=60):
    df = pd.read_sql("SELECT * FROM bars ORDER BY ts", engine, parse_dates=['ts'])
    df.set_index('ts', inplace=True)
    df['ret'] = df['close'].pct_change()
    df['ema_50'] = df['close'].ewm(span=50).mean()
    df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=14)
    df['rsi'] = ta.momentum.rsi(df['close'], window=14)
    # label: next 15-min return sign (example)
    df['label'] = (df['close'].shift(-15) / df['close'] - 1).shift(-0) > 0
    df.dropna(inplace=True)
    df.to_csv('data/features.csv')
    print("Saved data/features.csv")

if __name__ == '__main__':
    build_features()

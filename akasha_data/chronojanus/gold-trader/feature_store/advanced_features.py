import pandas as pd
from sqlalchemy import create_engine
import ta

engine = create_engine('postgresql://trader:example@localhost:5435/golddb')

def build_advanced_features(window=60):
    print("Fetching data from DB...")
    df = pd.read_sql("SELECT * FROM bars ORDER BY ts", engine, parse_dates=['ts'])
    df.set_index('ts', inplace=True)
    
    print("Calculating Technical Indicators...")
    # 1. Trend Indicators
    df['ema_12'] = ta.trend.ema_indicator(df['close'], window=12)
    df['ema_26'] = ta.trend.ema_indicator(df['close'], window=26)
    df['ema_50'] = ta.trend.ema_indicator(df['close'], window=50)
    df['ema_200'] = ta.trend.ema_indicator(df['close'], window=200)
    df['macd'] = ta.trend.macd_diff(df['close'])
    
    # 2. Momentum Indicators
    df['rsi'] = ta.momentum.rsi(df['close'], window=14)
    df['stoch_k'] = ta.momentum.stoch(df['high'], df['low'], df['close'], window=14, smooth_window=3)
    
    # 3. Volatility Indicators
    df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=14)
    df['bb_high'] = ta.volatility.bollinger_hband(df['close'], window=20, window_dev=2)
    df['bb_low'] = ta.volatility.bollinger_lband(df['close'], window=20, window_dev=2)
    df['bb_width'] = (df['bb_high'] - df['bb_low']) / df['close']
    
    # 4. Volume Indicators
    # Force volume to numeric, coerce errors to 0 (in case of 'None' or bad data)
    df['volume'] = pd.to_numeric(df['volume'], errors='coerce').fillna(0)
    df['obv'] = ta.volume.on_balance_volume(df['close'], df['volume'])

    # 5. Price Transforms
    df['ret_1'] = df['close'].pct_change()
    df['ret_5'] = df['close'].pct_change(5)
    
    # Targets (Labels)
    # Target 1: Direction (1 if price goes up in next 15 mins, 0 otherwise)
    df['target_dir'] = (df['close'].shift(-15) > df['close']).astype(int)
    # Target 2: Magnitude (Return over next 15 mins)
    df['target_ret'] = df['close'].shift(-15) / df['close'] - 1

    df.dropna(inplace=True)
    df.to_csv('data/advanced_features.csv')
    print(f"Saved data/advanced_features.csv with {len(df)} rows.")

if __name__ == '__main__':
    build_advanced_features()

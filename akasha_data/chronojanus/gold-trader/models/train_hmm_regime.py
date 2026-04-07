import pandas as pd
import numpy as np
from hmmlearn.hmm import GaussianHMM
import joblib

def train_hmm():
    print("Loading data for Regime Detection...")
    try:
        df = pd.read_csv('data/advanced_features.csv', parse_dates=['ts']).set_index('ts')
    except FileNotFoundError:
        print("Error: data/advanced_features.csv not found.")
        return

    # Use Returns and Volatility (ATR) to distinguish regimes
    # High Return + Low Vol = Steady Trend
    # High Vol + Low Return = Chop/Turning Point
    X = df[['ret_1', 'atr', 'rsi']].copy()
    X.fillna(0, inplace=True)

    print("Training HMM (3 Hidden States)...")
    # We assume 3 states: Uptrend, Downtrend, Sideways
    model = GaussianHMM(n_components=3, covariance_type="full", n_iter=100, random_state=42)
    model.fit(X)

    # Decode states to understand what they represent
    hidden_states = model.predict(X)
    df['state'] = hidden_states

    # Analyze states to label them heuristically
    state_means = []
    for i in range(3):
        mean_ret = df[df['state'] == i]['ret_1'].mean()
        print(f"State {i}: Mean Return = {mean_ret:.6f}")
        state_means.append((mean_ret, i))
    
    # Sort by return: Lowest (Bear), Middle (Neutral), Highest (Bull)
    state_means.sort()
    bear_state = state_means[0][1]
    bull_state = state_means[2][1]
    # The remaining one is Neutral
    
    mapping = {bear_state: -1, bull_state: 1} # others 0
    
    print(f"Regime Map: State {bull_state} -> Bullish, State {bear_state} -> Bearish, Others -> Neutral")
    
    joblib.dump((model, mapping), 'models/hmm_regime.pkl')
    print("HMM Regime model saved to models/hmm_regime.pkl")

if __name__ == '__main__':
    train_hmm()

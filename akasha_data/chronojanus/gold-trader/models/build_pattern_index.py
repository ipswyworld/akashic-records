import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
import joblib

def build_pattern_index():
    print("Loading data for Pattern Matching...")
    try:
        df = pd.read_csv('data/advanced_features.csv', parse_dates=['ts']).set_index('ts')
    except FileNotFoundError:
        print("Run feature_store/advanced_features.py first.")
        return

    # We will match based on normalized price shape of the last 60 bars (1 hour)
    # To do this, we create a rolling window dataset
    window_size = 60
    
    # Use 'close' price
    prices = df['close'].values
    
    # Prepare windows
    # We want to store: Window (X) -> Outcome (y, e.g., return over next 10 bars)
    X = []
    y = []
    indices = []
    
    print("Building historical windows (this may take a moment)...")
    for i in range(len(prices) - window_size - 10):
        window = prices[i : i + window_size]
        
        # Normalize window: (Price - Min) / (Max - Min) to match shape, not absolute price
        w_min, w_max = window.min(), window.max()
        if w_max == w_min: continue # Skip flat lines
        
        normalized_window = (window - w_min) / (w_max - w_min)
        
        # Outcome: Return over next 10 bars
        future_price = prices[i + window_size + 9]
        current_price = prices[i + window_size - 1]
        outcome = (future_price - current_price) / current_price
        
        X.append(normalized_window)
        y.append(outcome)
        indices.append(df.index[i + window_size - 1])
        
    X = np.array(X)
    y = np.array(y)
    
    print(f"Indexed {len(X)} historical patterns.")
    
    # Train KNN for fast similarity search
    knn = NearestNeighbors(n_neighbors=10, metric='euclidean', n_jobs=-1)
    knn.fit(X)
    
    # Save the index and the outcomes
    joblib.dump((knn, X, y), 'models/pattern_index.pkl')
    print("Pattern Index saved to models/pattern_index.pkl")

if __name__ == '__main__':
    build_pattern_index()

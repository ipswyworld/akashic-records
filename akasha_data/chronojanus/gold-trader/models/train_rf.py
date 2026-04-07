import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import classification_report
import joblib

def train_rf():
    print("Loading data...")
    try:
        df = pd.read_csv('data/advanced_features.csv', parse_dates=['ts']).set_index('ts')
    except FileNotFoundError:
        print("Error: data/advanced_features.csv not found. Run feature_store/advanced_features.py first.")
        return

    # Features and Target
    features = ['ema_12', 'ema_26', 'rsi', 'stoch_k', 'atr', 'bb_width', 'obv', 'ret_1', 'ret_5']
    target = 'target_dir'
    
    X = df[features].replace([float('inf'), -float('inf')], 0).fillna(0)
    y = df[target]

    print("Training Random Forest...")
    # TimeSeriesSplit for validation
    tscv = TimeSeriesSplit(n_splits=3)
    model = RandomForestClassifier(n_estimators=200, max_depth=10, min_samples_split=10, n_jobs=-1, random_state=42)
    
    for train_index, test_index in tscv.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]
        model.fit(X_train, y_train)
        print(f"Fold Score: {model.score(X_test, y_test):.4f}")

    # Final fit on all data
    model.fit(X, y)
    
    joblib.dump(model, 'models/rf_model.pkl')
    print("Random Forest model saved to models/rf_model.pkl")

if __name__ == '__main__':
    train_rf()

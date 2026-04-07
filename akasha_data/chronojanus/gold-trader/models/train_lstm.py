import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import StandardScaler
import joblib

def create_sequences(X, y, time_steps=10):
    Xs, ys = [], []
    for i in range(len(X) - time_steps):
        Xs.append(X[i:(i + time_steps)])
        ys.append(y[i + time_steps])
    return np.array(Xs), np.array(ys)

def train_lstm():
    print("Loading data...")
    try:
        df = pd.read_csv('data/advanced_features.csv', parse_dates=['ts']).set_index('ts')
    except FileNotFoundError:
        print("Run feature_store/advanced_features.py first.")
        return

    features = ['ema_12', 'rsi', 'ret_1', 'volatility', 'close'] 
    # Note: ensure these columns exist. 
    # Let's map to what we actually have in advanced_features.csv
    actual_features = ['ema_12', 'rsi', 'ret_1', 'bb_width', 'close']
    
    data = df[actual_features].values
    target = df['target_dir'].values

    # Scaling is crucial for LSTM
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data)
    
    joblib.dump(scaler, 'models/lstm_scaler.pkl')

    time_steps = 10
    X, y = create_sequences(data_scaled, target, time_steps)
    
    # Split
    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    print("Building LSTM...")
    model = Sequential([
        LSTM(50, return_sequences=False, input_shape=(X_train.shape[1], X_train.shape[2])),
        Dropout(0.2),
        Dense(1, activation='sigmoid')
    ])
    
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    
    print("Training...")
    model.fit(X_train, y_train, epochs=5, batch_size=32, validation_data=(X_test, y_test))
    
    model.save('models/lstm_model.h5')
    print("LSTM model saved to models/lstm_model.h5")

if __name__ == '__main__':
    train_lstm()

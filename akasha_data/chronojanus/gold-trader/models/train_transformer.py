import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
import joblib

def transformer_encoder(inputs, head_size, num_heads, ff_dim, dropout=0):
    # Attention and Normalization
    x = layers.MultiHeadAttention(key_dim=head_size, num_heads=num_heads, dropout=dropout)(inputs, inputs)
    x = layers.Dropout(dropout)(x)
    x = layers.LayerNormalization(epsilon=1e-6)(x)
    res = x + inputs

    # Feed Forward Part
    x = layers.Conv1D(filters=ff_dim, kernel_size=1, activation="relu")(res)
    x = layers.Dropout(dropout)(x)
    x = layers.Conv1D(filters=inputs.shape[-1], kernel_size=1)(x)
    x = layers.LayerNormalization(epsilon=1e-6)(x)
    return x + res

def train_transformer():
    print("Loading data for Transformer...")
    try:
        df = pd.read_csv('data/advanced_features.csv', parse_dates=['ts']).set_index('ts')
    except FileNotFoundError:
        print("Run feature_store/advanced_features.py first.")
        return

    features = ['ema_12', 'ema_50', 'rsi', 'macd', 'ret_1']
    data = df[features].fillna(0).values
    
    # Target: Predict price 5 steps ahead relative to now
    # (Close(+5) - Close(0)) / Close(0)
    # We need to reconstruct this target since 'target_ret' in csv is usually 1-step or fixed.
    # Let's re-calculate a specific 5-step trend target
    future_ret = (df['close'].shift(-5) / df['close']) - 1
    target = (future_ret > 0).astype(int).values # 1 if Up in 5 mins, 0 else

    # Trim NaNs from shift
    data = data[:-5]
    target = target[:-5]

    # Scaling
    scaler = tf.keras.layers.Normalization()
    scaler.adapt(data)
    
    # Create Sequences
    time_steps = 20
    X_seq, y_seq = [], []
    for i in range(len(data) - time_steps):
        X_seq.append(data[i : i+time_steps])
        y_seq.append(target[i+time_steps])
    
    X_seq = np.array(X_seq)
    y_seq = np.array(y_seq)

    # Build Transformer Model
    input_shape = X_seq.shape[1:]
    inputs = layers.Input(shape=input_shape)
    x = scaler(inputs)
    x = transformer_encoder(x, head_size=64, num_heads=4, ff_dim=64, dropout=0.1)
    x = layers.GlobalAveragePooling1D()(x)
    x = layers.Dropout(0.1)(x)
    x = layers.Dense(32, activation="relu")(x)
    outputs = layers.Dense(1, activation="sigmoid")(x)

    model = models.Model(inputs, outputs)
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

    print("Training Transformer...")
    model.fit(X_seq, y_seq, epochs=5, batch_size=64, validation_split=0.2)
    
    model.save('models/transformer_model.h5')
    print("Transformer model saved to models/transformer_model.h5")

if __name__ == '__main__':
    train_transformer()

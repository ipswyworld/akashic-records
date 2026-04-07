import pandas as pd
from sklearn.model_selection import TimeSeriesSplit
import xgboost as xgb
import joblib

df = pd.read_csv('data/features.csv', parse_dates=['ts']).set_index('ts')
X = df[['ema_50','atr','rsi']].values
y = df['label'].astype(int).values

tss = TimeSeriesSplit(n_splits=5)
model = xgb.XGBClassifier(n_estimators=100, max_depth=4, use_label_encoder=False, eval_metric='logloss')
model.fit(X, y)
joblib.dump(model, 'models/xgb_baseline.pkl')
print("Model saved to models/xgb_baseline.pkl")

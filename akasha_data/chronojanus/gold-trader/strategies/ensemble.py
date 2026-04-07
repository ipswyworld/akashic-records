from .base_strategy import BaseStrategy
from .trend_following import TrendFollowingStrategy
from .mean_reversion import MeanReversionStrategy
from .breakout import BreakoutStrategy
from .predictive_trend import PredictiveTrendStrategy
from .pattern_match import PatternMatchingStrategy
from .hall_of_fame import HallOfFameStrategy
from .math_models import MathPredictiveStrategy
import joblib
import pandas as pd
import numpy as np

class EnsembleStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("Ensemble_Meta")
        self.strategies = [
            TrendFollowingStrategy(),
            MeanReversionStrategy(),
            BreakoutStrategy(),
            PredictiveTrendStrategy(),
            PatternMatchingStrategy(),
            HallOfFameStrategy(),
            MathPredictiveStrategy()
        ]
        try:
            self.rf_model = joblib.load('models/rf_model.pkl')
            self.has_rf = True
        except:
            self.has_rf = False
            print("Warning: RF model not found.")

    def generate_signals(self, df):
        # 1. Collect votes from rule-based strategies
        votes = pd.DataFrame(index=df.index)
        for strat in self.strategies:
            votes[strat.name] = strat.generate_signals(df)
            
        # 2. Add ML vote
        if self.has_rf:
            features = ['ema_12', 'ema_26', 'rsi', 'stoch_k', 'atr', 'bb_width', 'obv', 'ret_1', 'ret_5']
            # fill missing with 0 for safety
            X = df[features].replace([np.inf, -np.inf], 0).fillna(0)
            rf_pred = self.rf_model.predict(X)
            # Map 0/1 to -1/1 (assuming model predicts direction 1=up, 0=down/stable? 
            # In train_rf, target_dir is 1 (up) or 0 (down). 
            # Let's map 0 -> -1 for the vote.
            votes['RF_Model'] = np.where(rf_pred == 1, 1, -1)
            
        # 3. Simple Majority Vote
        # Sum across columns
        total_vote = votes.sum(axis=1)
        
        # Threshold: if sum > 0 -> Buy (1), < 0 -> Sell (-1), else 0
        final_signal = total_vote.apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
        
        return final_signal

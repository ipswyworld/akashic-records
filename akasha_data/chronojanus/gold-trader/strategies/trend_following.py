from .base_strategy import BaseStrategy

class TrendFollowingStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("TrendFollowing_EMA_Cross")

    def generate_signals(self, df):
        signals = df.copy()
        signals['signal'] = 0
        
        # Golden Cross / Death Cross logic (using 50 and 200 EMA)
        # Buy when EMA 50 > EMA 200 (Uptrend)
        # Sell when EMA 50 < EMA 200 (Downtrend)
        
        # Filter: Only trade if ADX (trend strength) > 25 (if available) - simplifying here to just EMA
        
        signals.loc[signals['ema_50'] > signals['ema_200'], 'signal'] = 1
        signals.loc[signals['ema_50'] < signals['ema_200'], 'signal'] = -1
        
        return signals['signal']

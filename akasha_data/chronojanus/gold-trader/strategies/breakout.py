from .base_strategy import BaseStrategy

class BreakoutStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("Breakout_Donchian")

    def generate_signals(self, df):
        signals = df.copy()
        signals['signal'] = 0
        
        # Donchian Channels (20-period High/Low)
        # Implied calculation since we might not have it in CSV yet, or we assume it's calculated here
        # For efficiency, let's calculate rolling max/min here if not present
        
        high_20 = signals['high'].rolling(window=20).max()
        low_20 = signals['low'].rolling(window=20).min()
        
        # Buy: Close > Previous 20-period High
        signals.loc[signals['close'] > high_20.shift(1), 'signal'] = 1
        
        # Sell: Close < Previous 20-period Low
        signals.loc[signals['close'] < low_20.shift(1), 'signal'] = -1
        
        return signals['signal']

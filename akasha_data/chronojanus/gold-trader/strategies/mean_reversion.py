from .base_strategy import BaseStrategy

class MeanReversionStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("MeanReversion_BB_RSI")

    def generate_signals(self, df):
        signals = df.copy()
        signals['signal'] = 0
        
        # Buy: Price < Lower Bollinger Band AND RSI < 30 (Oversold)
        buy_cond = (signals['close'] < signals['bb_low']) & (signals['rsi'] < 30)
        
        # Sell: Price > Upper Bollinger Band AND RSI > 70 (Overbought)
        sell_cond = (signals['close'] > signals['bb_high']) & (signals['rsi'] > 70)
        
        signals.loc[buy_cond, 'signal'] = 1
        signals.loc[sell_cond, 'signal'] = -1
        
        return signals['signal']

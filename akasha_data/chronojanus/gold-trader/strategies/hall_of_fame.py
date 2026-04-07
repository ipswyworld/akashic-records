from .base_strategy import BaseStrategy
import pandas as pd
import ta

class HallOfFameStrategy(BaseStrategy):
    """
    Implements 10 classic strategies and returns a consensus signal.
    """
    def __init__(self):
        super().__init__("Hall_of_Fame_10")

    def generate_signals(self, df):
        # We calculate 10 different signals and average them
        
        close = df['close']
        high = df['high']
        low = df['low']
        
        # 1. SMA Crossover (Fast)
        sma_50 = ta.trend.sma_indicator(close, window=50)
        sma_200 = ta.trend.sma_indicator(close, window=200)
        s1 = (sma_50 > sma_200).astype(int).replace(0, -1)
        
        # 2. RSI Mean Reversion
        rsi = ta.momentum.rsi(close, window=14)
        s2 = pd.Series(0, index=df.index)
        s2[rsi < 30] = 1
        s2[rsi > 70] = -1
        
        # 3. MACD
        macd = ta.trend.macd_diff(close)
        s3 = (macd > 0).astype(int).replace(0, -1)
        
        # 4. Bollinger Bands Breakout/Reversal
        bb_h = ta.volatility.bollinger_hband(close, window=20)
        bb_l = ta.volatility.bollinger_lband(close, window=20)
        s4 = pd.Series(0, index=df.index)
        s4[close < bb_l] = 1 # Buy dip
        s4[close > bb_h] = -1 # Sell rip
        
        # 5. Stochastic Oscillator
        stoch = ta.momentum.stoch(high, low, close, window=14)
        s5 = pd.Series(0, index=df.index)
        s5[stoch < 20] = 1
        s5[stoch > 80] = -1
        
        # 6. Commodity Channel Index (CCI)
        cci = ta.trend.cci(high, low, close, window=20)
        s6 = pd.Series(0, index=df.index)
        s6[cci < -100] = 1
        s6[cci > 100] = -1
        
        # 7. Parabolic SAR (Trend)
        # TA lib implementation returns the value, we need to compare to price
        psar = ta.trend.psar_down(high, low, close, step=0.02, max_step=0.2)
        psar_up = ta.trend.psar_up(high, low, close, step=0.02, max_step=0.2)
        s7 = pd.Series(0, index=df.index)
        s7[close > psar_up.fillna(0)] = 1
        s7[close < psar.fillna(999999)] = -1

        # 8. Williams %R
        wr = ta.momentum.williams_r(high, low, close, lbp=14)
        s8 = pd.Series(0, index=df.index)
        s8[wr < -80] = 1
        s8[wr > -20] = -1
        
        # 9. Awesome Oscillator
        ao = ta.momentum.awesome_oscillator(high, low)
        s9 = (ao > 0).astype(int).replace(0, -1)
        
        # 10. Momentum (Rate of Change)
        roc = ta.momentum.roc(close, window=12)
        s10 = (roc > 0).astype(int).replace(0, -1)

        # --- NEW 10 STRATEGIES ---

        # 11. ADX (Trend Strength)
        # Buy if ADX > 25 (Trend) AND +DI > -DI
        adx = ta.trend.adx(high, low, close, window=14)
        plus_di = ta.trend.adx_pos(high, low, close, window=14)
        minus_di = ta.trend.adx_neg(high, low, close, window=14)
        s11 = pd.Series(0, index=df.index)
        s11[(adx > 25) & (plus_di > minus_di)] = 1
        s11[(adx > 25) & (plus_di < minus_di)] = -1

        # 12. Ichimoku Cloud (Simplified)
        # Buy if Close > Span A and Span B
        ichimoku_a = ta.trend.ichimoku_a(high, low, window1=9, window2=26).shift(26) # forward projected, shift back to compare current
        ichimoku_b = ta.trend.ichimoku_b(high, low, window2=26, window3=52).shift(26)
        # Note: 'shift' in pandas moves data. In Ichimoku, the cloud is plotted forward. 
        # To compare current price to "current cloud", we just use the calculated values.
        # library ta calculates it aligned.
        s12 = pd.Series(0, index=df.index)
        s12[(close > ichimoku_a) & (close > ichimoku_b)] = 1
        s12[(close < ichimoku_a) & (close < ichimoku_b)] = -1

        # 13. Keltner Channels
        # Buy if Close > Upper, Sell if Close < Lower
        keltner_h = ta.volatility.keltner_channel_hband(high, low, close, window=20)
        keltner_l = ta.volatility.keltner_channel_lband(high, low, close, window=20)
        s13 = pd.Series(0, index=df.index)
        s13[close > keltner_h] = 1
        s13[close < keltner_l] = -1

        # 14. Money Flow Index (MFI) - Volume weighted RSI
        mfi = ta.volume.money_flow_index(high, low, close, df['volume'], window=14)
        s14 = pd.Series(0, index=df.index)
        s14[mfi < 20] = 1
        s14[mfi > 80] = -1

        # 15. On-Balance Volume (OBV)
        # Signal based on OBV EMA crossover
        obv = ta.volume.on_balance_volume(close, df['volume'])
        obv_ema = ta.trend.ema_indicator(obv, window=20)
        s15 = (obv > obv_ema).astype(int).replace(0, -1)

        # 16. TRIX (Triple Exponential Average)
        trix = ta.trend.trix(close, window=15)
        s16 = (trix > 0).astype(int).replace(0, -1)

        # 17. Ultimate Oscillator
        uo = ta.momentum.ultimate_oscillator(high, low, close)
        s17 = pd.Series(0, index=df.index)
        s17[uo < 30] = 1
        s17[uo > 70] = -1

        # 18. Chaikin Money Flow (CMF)
        cmf = ta.volume.chaikin_money_flow(high, low, close, df['volume'], window=20)
        s18 = (cmf > 0).astype(int).replace(0, -1)

        # 19. Vortex Indicator
        vip = ta.trend.vortex_indicator_pos(high, low, close, window=14)
        vin = ta.trend.vortex_indicator_neg(high, low, close, window=14)
        s19 = pd.Series(0, index=df.index)
        s19[vip > vin] = 1
        s19[vip < vin] = -1

        # 20. Mass Index (Reversal)
        # If Mass Index > 25 and then creates "reversal bulge", simpler: just mean reversion threshold
        mass = ta.trend.mass_index(high, low, window_fast=9, window_slow=25)
        s20 = pd.Series(0, index=df.index)
        s20[mass > 25] = -1 # Likely reversal
        
        # Consensus of 20 Strategies
        total = s1 + s2 + s3 + s4 + s5 + s6 + s7 + s8 + s9 + s10 + \
                s11 + s12 + s13 + s14 + s15 + s16 + s17 + s18 + s19 + s20
        
        # Higher threshold for 20 votes. Let's say +/- 6 for strong agreement.
        final_signal = pd.Series(0, index=df.index)
        final_signal[total >= 6] = 1
        final_signal[total <= -6] = -1
        
        return final_signal

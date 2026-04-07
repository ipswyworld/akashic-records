import pandas as pd
import numpy as np

class BaseStrategy:
    def __init__(self, name):
        self.name = name

    def generate_signals(self, df):
        """
        Takes a DataFrame with features and returns a DataFrame with a 'signal' column.
        Signal: 1 (Buy), -1 (Sell), 0 (Neutral)
        """
        raise NotImplementedError("Strategies must implement generate_signals")

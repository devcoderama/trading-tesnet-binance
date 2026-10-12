import pandas as pd

class SimpleStrategy:
    """SMA crossover strategy: fast SMA crosses slow SMA."""
    def __init__(self, fast=9, slow=21):
        self.fast = fast
        self.slow = slow

    def signal(self, df: pd.DataFrame):
        if len(df) < self.slow + 1:
            return "HOLD"
        df = df.copy()
        df["fast"] = df["close"].rolling(self.fast).mean()
        df["slow"] = df["close"].rolling(self.slow).mean()
        prev_fast = df["fast"].iloc[-2]
        prev_slow = df["slow"].iloc[-2]
        curr_fast = df["fast"].iloc[-1]
        curr_slow = df["slow"].iloc[-1]
        if prev_fast <= prev_slow and curr_fast > curr_slow:
            return "BUY"
        if prev_fast >= prev_slow and curr_fast < curr_slow:
            return "SELL"
        return "HOLD"

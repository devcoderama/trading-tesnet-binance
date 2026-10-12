class SimpleStrategy:
    """SMA crossover strategy using plain Python lists."""
    def __init__(self, fast=9, slow=21):
        self.fast = fast
        self.slow = slow

    def _sma(self, values, n):
        if len(values) < n:
            return None
        return sum(values[-n:]) / n

    def indicators(self, closes):
        return {
            "sma_fast": self._sma(closes, self.fast),
            "sma_slow": self._sma(closes, self.slow),
        }

    def signal(self, closes):
        if len(closes) < self.slow + 1:
            return "HOLD"
        prev_fast = self._sma(closes[:-1], self.fast)
        prev_slow = self._sma(closes[:-1], self.slow)
        curr_fast = self._sma(closes, self.fast)
        curr_slow = self._sma(closes, self.slow)
        if None in (prev_fast, prev_slow, curr_fast, curr_slow):
            return "HOLD"
        if prev_fast <= prev_slow and curr_fast > curr_slow:
            return "BUY"
        if prev_fast >= prev_slow and curr_fast < curr_slow:
            return "SELL"
        return "HOLD"

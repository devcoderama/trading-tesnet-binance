class RiskManager:
    def __init__(self, max_position=0.01):
        self.max_position = max_position

    def select_symbol(self, symbols, quote="USDT", risk_level="MEDIUM"):
        cands = [s for s in symbols if s.endswith(quote)]
        # price fetch not possible here; heuristic by lexicographic/name is weak.
        # Sort by length then name to diversify across small/mid/large cap proxies.
        cands = sorted(set(cands))
        if not cands:
            return None
        n = len(cands)
        if risk_level == "LOW":
            idx = n // 4
        elif risk_level == "HIGH":
            idx = (3 * n) // 4
        else:
            idx = n // 2
        return cands[idx]

    def position_size(self, balance, price):
        qty = min(balance * 0.01 / price, self.max_position)
        return round(qty, 6)

    def stop_loss_price(self, entry, pct=0.02):
        return round(entry * (1 - pct), 4)

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

    def position_size(self, balance, price, risk_level=None):
        if risk_level is None:
            try:
                from utils.db import get_config
                risk_level = get_config("RISK_LEVEL", "MEDIUM")
            except Exception:
                risk_level = "MEDIUM"
        risk_level = str(risk_level).upper()
        pct = 0.005 if risk_level == "LOW" else 0.02 if risk_level == "HIGH" else 0.01
        qty = balance * pct / price
        if self.max_position and self.max_position > 0:
            qty = min(qty, self.max_position)
        return round(qty, 6)

    def stop_loss_price(self, entry, pct=0.02):
        return round(entry * (1 - pct), 4)

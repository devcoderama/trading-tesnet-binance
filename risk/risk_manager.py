class RiskManager:
    def __init__(self, max_position=0.01):
        self.max_position = max_position

    def position_size(self, balance, price):
        qty = min(balance * 0.01 / price, self.max_position)
        return round(qty, 6)

    def stop_loss_price(self, entry, pct=0.02):
        return round(entry * (1 - pct), 4)

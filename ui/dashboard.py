from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

def render_dashboard(symbol, risk_level, interval, price, signal, cur_bal, prev_bal, dry_run, testnet, history):
    t = Table(title="Bot Status", box=box.ROUNDED)
    t.add_column("Key", style="cyan")
    t.add_column("Value", style="green")
    t.add_row("Symbol", symbol)
    t.add_row("Interval", interval)
    t.add_row("Risk Level", risk_level)
    t.add_row("Price", str(price))
    t.add_row("Signal", signal)
    t.add_row("Balance Now (USDT)", f"{cur_bal:.4f}")
    t.add_row("Balance Prev (USDT)", f"{prev_bal:.4f}" if prev_bal is not None else "-")
    t.add_row("Dry Run", str(dry_run))
    t.add_row("Testnet", str(testnet))
    console.clear()
    console.print(Panel(t, title="Binance Testnet Bot", border_style="blue"))

    if history:
        h = Table(title="Trade History", box=box.SIMPLE)
        h.add_column("Time", style="dim")
        h.add_column("Side")
        h.add_column("Symbol")
        h.add_column("Qty")
        h.add_column("Status")
        for row in history[-10:]:
            h.add_row(*[str(x) for x in row])
        console.print(h)

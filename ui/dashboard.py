from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

def render_dashboard(info, rows, history):
    g = Table(box=box.ROUNDED, title="Bot Info")
    g.add_column("Key", style="cyan")
    g.add_column("Value", style="green")
    for k, v in info.items():
        g.add_row(str(k), str(v))
    console.clear()
    console.print(Panel(g, title="Binance Bot", border_style="blue"))

    t = Table(title="Multi-Symbol Trading", box=box.ROUNDED)
    t.add_column("Symbol")
    t.add_column("Interval")
    t.add_column("Indicators")
    t.add_column("Price")
    t.add_column("Signal")
    t.add_column("Last Buy")
    t.add_column("Last Sell")
    for r in rows:
        ind = r.get("indicators", {})
        t.add_row(
            r.get("symbol", ""),
            r.get("interval", ""),
            f"SMA{r.get('fast',9)}={ind.get('sma_fast')} | SMA{r.get('slow',21)}={ind.get('sma_slow')}",
            str(r.get("price", "")),
            r.get("signal", ""),
            str(r.get("last_buy", "-")),
            str(r.get("last_sell", "-")),
        )
    console.print(t)

    if history:
        h = Table(title="Trade History", box=box.SIMPLE)
        h.add_column("Time")
        h.add_column("Side")
        h.add_column("Symbol")
        h.add_column("Qty")
        h.add_column("Status")
        for row in history[-10:]:
            h.add_row(*[str(x) for x in row])
        console.print(h)

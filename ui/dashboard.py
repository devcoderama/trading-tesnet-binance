from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

def render_dashboard(info, rows, history):
    g = Table(box=box.ROUNDED, title="[bold magenta]Bot Info[/bold magenta]")
    g.add_column("Key", style="cyan", justify="center")
    g.add_column("Value", style="green", justify="center")
    for k, v in info.items():
        g.add_row(str(k), str(v))
    console.clear()
    console.print(Panel(g, title="[bold blue]Binance Bot[/bold blue]", border_style="bright_magenta"))

    t = Table(title="[bold yellow]Multi-Symbol Trading[/bold yellow]", box=box.ROUNDED)
    for col in ["Symbol", "Interval", "Indicators", "Price", "Signal", "Last Buy", "Last Sell"]:
        t.add_column(col, style="bright_cyan", justify="center")
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
        h = Table(title="[bold green]Trade History[/bold green]", box=box.SIMPLE)
        for col in ["Time", "Side", "Symbol", "Qty", "Status"]:
            h.add_column(col, style="bright_yellow", justify="center")
        for row in history[-10:]:
            h.add_row(*[str(x) for x in row])
        console.print(h)

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime

console = Console()

def log_inference_dashboard(mci_val, emissions_val, latency):
    mci_status = "[bold green]HIGHLY CIRCULAR[/]" if mci_val > 0.7 else \
                 ("[bold yellow]TRANSITIONAL[/]" if mci_val > 0.3 else "[bold red]LINEAR (WASTE-PRONE)[/]")
    
    emi_status = "[bold green]LOW IMPACT[/]" if emissions_val < 2.0 else \
                 ("[bold red]CRITICAL EMISSIONS[/]")

    table = Table(show_header=True, header_style="bold magenta", border_style="dim")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right", style="bold white")
    table.add_column("Assessment", justify="center")

    table.add_row("MCI Score", f"{mci_val:.4f}", mci_status)
    table.add_row("CO2 Emissions", f"{emissions_val:.4f} kg/kg", emi_status)
    table.add_row("Inference Latency", f"{latency}ms", "⚡ Optimized")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    console.print("\n")
    console.print(Panel(
        table, 
        title=f"[bold white]ML INFERENCE ENGINE[/] | {timestamp}", 
        subtitle="[dim]Project: Circular Economy Analytics[/]",
        border_style="blue",
        expand=False
    ))
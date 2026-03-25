"""
╔══════════════════════════════════════════════════════════════╗
║       Metallurgy LCA — Interactive Prediction Client        ║
║         Circular Economy Analytics • v1.0                   ║
╚══════════════════════════════════════════════════════════════╝

A professional CLI tool for querying the LCA prediction API.
Sends material data and displays MCI & emissions predictions
with a rich, color-coded terminal dashboard.

Usage:
    python interactive_client.py
"""

import requests
import time
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, FloatPrompt
from rich.text import Text
from rich.columns import Columns
from rich.rule import Rule
from rich import box

console = Console()
API_URL = "http://127.0.0.1:8000/api/v1/predict"

# ─── Dropdown-style options ──────────────────────────────────────────────────

MATERIALS = ["Aluminum", "Copper", "Steel", "Zinc", "Nickel", "Titanium", "Lead", "Tin"]
ROUTES = ["Primary", "Secondary"]
EOL_ROUTES = ["Recycled", "Landfill", "Incineration", "Reuse"]
TRANSPORT_MODES = ["Truck", "Rail", "Ship", "Truck+Ship", "Rail+Ship", "Air"]

# ─── Feature definitions with defaults, ranges, and units ────────────────────

NUMERIC_FIELDS = [
    # (key, display_name, unit, default, min, max)
    ("mining_energy_MJ_per_kg",           "Mining Energy",              "MJ/kg",  5.0,   0.0, 100.0),
    ("smelting_energy_MJ_per_kg",         "Smelting Energy",            "MJ/kg", 10.0,   0.0, 200.0),
    ("refining_energy_MJ_per_kg",         "Refining Energy",            "MJ/kg",  5.0,   0.0, 100.0),
    ("fabrication_energy_MJ_per_kg",      "Fabrication Energy",         "MJ/kg",  3.0,   0.0,  50.0),
    ("recycled_content_frac",             "Recycled Content",           "frac",   0.2,   0.0,   1.0),
    ("recycling_efficiency_frac",         "Recycling Efficiency",       "frac",   0.5,   0.0,   1.0),
    ("recycled_output_kg_per_kg",         "Recycled Output",            "kg/kg",  0.3,   0.0,   1.0),
    ("loop_closing_potential_USD_per_kg", "Loop Closing Potential",     "$/kg",   0.1,   0.0,  10.0),
    ("reuse_potential_score",             "Reuse Potential",            "score",  0.5,   0.0,   1.0),
    ("repairability_score",               "Repairability",              "score",  0.5,   0.0,   1.0),
    ("product_lifetime_years",            "Product Lifetime",           "years", 10.0,   0.1,  50.0),
    ("transport_distance_km",             "Transport Distance",         "km",   500.0,   0.0, 20000.0),
    ("electricity_grid_renewable_pct",    "Grid Renewable Share",       "%",     40.0,   0.0, 100.0),
    ("renewable_electricity_frac",        "Renewable Electricity",      "frac",   0.4,   0.0,   1.0),
    ("material_criticality_score",        "Material Criticality",       "score",  0.3,   0.0,   1.0),
]


def print_banner():
    """Display the startup banner."""
    banner = Text()
    banner.append("◆ ", style="bright_cyan")
    banner.append("Metallurgy LCA", style="bold bright_white")
    banner.append("  —  ", style="dim")
    banner.append("Interactive Prediction Client", style="italic bright_cyan")

    console.print()
    console.print(Panel(
        banner,
        border_style="bright_cyan",
        box=box.DOUBLE_EDGE,
        subtitle="[dim]Circular Economy Analytics Engine • v1.0[/]",
        subtitle_align="right",
        padding=(1, 3),
    ))
    console.print()


def choose_option(label, options, default_idx=0):
    """Render a numbered menu and return the selected value."""
    console.print(f"  [bold bright_cyan]{label}[/]")
    for i, opt in enumerate(options):
        marker = "›" if i == default_idx else " "
        style = "bold bright_white" if i == default_idx else "white"
        console.print(f"    [{style}]{marker} {i + 1}. {opt}[/]")

    while True:
        choice = Prompt.ask(
            f"    [dim]Select[/] [bright_cyan]\\[1-{len(options)}][/]",
            default=str(default_idx + 1),
        )
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                console.print(f"    [green]✔[/] {options[idx]}\n")
                return options[idx]
        except ValueError:
            pass
        console.print("    [red]Invalid choice, try again.[/]")


def get_numeric_input(field_key, display_name, unit, default, min_val, max_val):
    """Prompt for a numeric value with validation and range hints."""
    hint = f"[dim]{min_val}–{max_val} {unit}[/]"
    while True:
        try:
            val = FloatPrompt.ask(
                f"    [bright_cyan]{display_name}[/] {hint}",
                default=default,
            )
            if min_val <= val <= max_val:
                return val
            console.print(f"    [red]Out of range. Must be {min_val}–{max_val}.[/]")
        except Exception:
            console.print("    [red]Please enter a valid number.[/]")


def collect_inputs():
    """Walk the user through all 19 input fields and return a payload dict."""
    payload = {}

    # ── Section 1: Material Identity ─────────────────────────────────────
    console.print(Rule("[bold bright_magenta]① Material Identity[/]", style="bright_magenta"))
    console.print()
    payload["material"] = choose_option("Material Type", MATERIALS, default_idx=0)
    payload["route"] = choose_option("Production Route", ROUTES, default_idx=0)

    # ── Section 2: Energy Profile ────────────────────────────────────────
    console.print(Rule("[bold bright_magenta]② Energy Profile[/]", style="bright_magenta"))
    console.print()
    for key, name, unit, default, mn, mx in NUMERIC_FIELDS[:4]:
        payload[key] = get_numeric_input(key, name, unit, default, mn, mx)
    console.print()

    # ── Section 3: Circularity Metrics ───────────────────────────────────
    console.print(Rule("[bold bright_magenta]③ Circularity Metrics[/]", style="bright_magenta"))
    console.print()
    for key, name, unit, default, mn, mx in NUMERIC_FIELDS[4:11]:
        payload[key] = get_numeric_input(key, name, unit, default, mn, mx)
    console.print()

    # ── Section 4: End-of-Life & Transport ───────────────────────────────
    console.print(Rule("[bold bright_magenta]④ End-of-Life & Transport[/]", style="bright_magenta"))
    console.print()
    payload["end_of_life_route"] = choose_option("End-of-Life Route", EOL_ROUTES, default_idx=0)
    payload["transport_distance_km"] = get_numeric_input(*NUMERIC_FIELDS[11])
    payload["transport_mode"] = choose_option("Transport Mode", TRANSPORT_MODES, default_idx=0)
    console.print()

    # ── Section 5: Grid & Criticality ────────────────────────────────────
    console.print(Rule("[bold bright_magenta]⑤ Grid & Material Criticality[/]", style="bright_magenta"))
    console.print()
    for key, name, unit, default, mn, mx in NUMERIC_FIELDS[12:]:
        payload[key] = get_numeric_input(key, name, unit, default, mn, mx)
    console.print()

    return payload


def display_input_summary(payload):
    """Show a formatted summary table of the collected inputs."""
    table = Table(
        title="Input Summary",
        box=box.ROUNDED,
        border_style="bright_cyan",
        title_style="bold bright_white",
        show_lines=True,
        padding=(0, 1),
    )
    table.add_column("Parameter", style="cyan", min_width=28)
    table.add_column("Value", style="bold bright_white", justify="right", min_width=14)

    for key, value in payload.items():
        display_key = key.replace("_", " ").title()
        if isinstance(value, float):
            table.add_row(display_key, f"{value:,.4f}")
        else:
            table.add_row(display_key, str(value))

    console.print(table)
    console.print()


def display_prediction(result, latency_s):
    """Render the prediction result in a professional dashboard panel."""
    data = result["data"]["predictions"]
    mci = data["MCI_score"]
    emissions = data["emissions_kgCO2e"]

    # MCI Assessment
    if mci > 0.7:
        mci_style, mci_label = "bold bright_green", "● HIGHLY CIRCULAR"
    elif mci > 0.3:
        mci_style, mci_label = "bold bright_yellow", "● TRANSITIONAL"
    else:
        mci_style, mci_label = "bold bright_red", "● LINEAR (WASTE-PRONE)"

    # Emissions Assessment
    if emissions < 2.0:
        emi_style, emi_label = "bold bright_green", "● LOW IMPACT"
    elif emissions < 5.0:
        emi_style, emi_label = "bold bright_yellow", "● MODERATE IMPACT"
    else:
        emi_style, emi_label = "bold bright_red", "● CRITICAL EMISSIONS"

    # Build results table
    table = Table(box=box.HEAVY_EDGE, border_style="bright_blue", show_header=True,
                  header_style="bold bright_magenta", padding=(0, 2))
    table.add_column("Metric", style="bright_cyan", min_width=22)
    table.add_column("Value", justify="right", style="bold bright_white", min_width=16)
    table.add_column("Assessment", justify="center", min_width=24)

    table.add_row("MCI Score", f"{mci:.4f}", Text(mci_label, style=mci_style))
    table.add_row("CO₂ Emissions", f"{emissions:.4f} kg/kg", Text(emi_label, style=emi_style))
    table.add_row("API Latency", f"{latency_s:.0f} ms", Text("⚡ Live", style="bold bright_cyan"))
    table.add_row("Transaction ID", result["transaction_id"], Text("✔ Logged", style="dim"))

    material = result["data"]["input_material"]
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    console.print(Panel(
        table,
        title=f"[bold bright_white]⬡  PREDICTION RESULT  ⬡[/]  [dim]|[/]  [bright_cyan]{material}[/]  [dim]|[/]  [dim]{timestamp}[/]",
        border_style="bright_blue",
        box=box.DOUBLE_EDGE,
        padding=(1, 2),
        subtitle="[dim]Powered by LCA Analytics Engine[/]",
        subtitle_align="right",
    ))


def send_prediction(payload):
    """Send payload to the API and display result."""
    console.print(Rule("[bold bright_yellow]⏳ Sending to API...[/]", style="bright_yellow"))
    console.print()

    try:
        start = time.perf_counter()
        response = requests.post(API_URL, json=payload, timeout=10)
        latency = (time.perf_counter() - start) * 1000

        if response.status_code == 200:
            result = response.json()
            display_prediction(result, latency)
        else:
            console.print(Panel(
                f"[bold red]HTTP {response.status_code}[/]\n{response.text}",
                title="[bold red]✖ API Error[/]",
                border_style="red",
            ))
    except requests.exceptions.ConnectionError:
        console.print(Panel(
            "[bold red]Could not connect to the API server.[/]\n"
            "[dim]Make sure the server is running:[/]  [bright_cyan]python app.py[/]",
            title="[bold red]✖ Connection Failed[/]",
            border_style="red",
            box=box.DOUBLE_EDGE,
        ))
    except requests.exceptions.Timeout:
        console.print(Panel(
            "[bold red]Request timed out after 10 seconds.[/]",
            title="[bold red]✖ Timeout[/]",
            border_style="red",
        ))


def main():
    print_banner()

    while True:
        try:
            # Collect input
            payload = collect_inputs()

            # Show summary
            display_input_summary(payload)

            # Confirm
            confirm = Prompt.ask(
                "  [bold bright_yellow]Send prediction?[/]",
                choices=["y", "n"],
                default="y",
            )

            if confirm == "y":
                send_prediction(payload)
            else:
                console.print("  [dim]Prediction cancelled.[/]")

            console.print()

            # Loop or exit
            again = Prompt.ask(
                "  [bold bright_cyan]Run another prediction?[/]",
                choices=["y", "n"],
                default="y",
            )
            if again != "y":
                break

            console.print()
            console.print(Rule("[dim]New Prediction[/]", style="dim"))
            console.print()

        except KeyboardInterrupt:
            console.print("\n  [dim]Interrupted. Exiting...[/]")
            break

    # Farewell
    console.print()
    console.print(Panel(
        "[bright_cyan]Thank you for using the LCA Prediction Client.[/]\n"
        "[dim]For API docs, visit:[/]  [link=http://127.0.0.1:8000/docs]http://127.0.0.1:8000/docs[/]",
        border_style="bright_cyan",
        box=box.DOUBLE_EDGE,
        padding=(1, 3),
    ))


if __name__ == "__main__":
    main()

"""
Metallurgy LCA — Unified Application
Circular Economy Analytics Engine • v1.0

Run this single file to use the entire LCA prediction system.
The API server starts automatically in the background.

Usage:
    python main.py
"""

import subprocess
import requests
import time
import sys
import os
import atexit
import threading
import uvicorn

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, FloatPrompt
from rich.text import Text
from rich.rule import Rule
from rich.align import Align
from rich import box

console = Console()
API_URL = "http://127.0.0.1:8000"
PREDICT_URL = f"{API_URL}/api/v1/predict"

_server_process = None


# ═════════════════════════════════════════════════════════════════════════
#   BRANDING
# ═════════════════════════════════════════════════════════════════════════

LOGO = r"""
[bright_cyan]    ╦   ╔═╗  ╔═╗     [bold bright_white]Life Cycle Assessment[/]
[bright_cyan]    ║   ║    ╠═╣     [dim]for Metallurgy & Circular Economy[/]
[bright_cyan]    ╩═╝ ╚═╝  ╩ ╩     [bright_green]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/][/bright_cyan]
"""


def show_splash():
    console.clear()
    console.print()
    console.print(Panel(
        Align.center(Text.from_markup(LOGO)),
        border_style="bright_cyan",
        box=box.DOUBLE_EDGE,
        padding=(1, 4),
        subtitle="[dim]AI-Powered Circular Economy Analytics[/]",
        subtitle_align="center",
    ))
    console.print()

    modules = Text.from_markup(
        "  [bright_cyan]◉[/] [bold]User Input Module[/]           Captures process parameters\n"
        "  [bright_yellow]◉[/] [bold]AI Prediction Engine[/]        ML-powered emissions & MCI scoring\n"
        "  [bright_green]◉[/] [bold]Circularity Metrics[/]         Recycling, reuse & loop closing potential\n"
        "  [bright_magenta]◉[/] [bold]Impact Assessment[/]           CO₂ footprint & environmental analysis\n"
        "  [bright_red]◉[/] [bold]Report Generation[/]           ESG-ready output & compliance reporting"
    )
    console.print(Panel(
        modules,
        title="[bold bright_white]Core Functional Modules[/]",
        border_style="dim cyan",
        box=box.ROUNDED,
        padding=(1, 3),
    ))
    console.print()

    highlights = Table(box=box.SIMPLE_HEAVY, border_style="dim", show_header=False, padding=(0, 2))
    highlights.add_column("", style="bright_cyan", min_width=30)
    highlights.add_column("", style="bright_cyan", min_width=30)
    highlights.add_row("🤖 AI-Based LCA Automation", "♻️  Circularity-Focused Metrics")
    highlights.add_row("🇮🇳 Indian Mining Relevance", "👤 Beginner-Friendly Design")
    console.print(Align.center(highlights))
    console.print()


# ═════════════════════════════════════════════════════════════════════════
#   SERVER MANAGEMENT (in-process via threading)
# ═════════════════════════════════════════════════════════════════════════

def is_server_running():
    try:
        return requests.get(API_URL, timeout=2).status_code == 200
    except Exception:
        return False


def start_server():
    global _server_thread, _uvicorn_server

    if is_server_running():
        console.print("  [green]✔[/] Prediction engine is online.\n")
        return True

    # Run uvicorn in a background daemon thread (same process = no pycache issues)
    config = uvicorn.Config("app:app", host="127.0.0.1", port=8000, log_level="warning")
    _uvicorn_server = uvicorn.Server(config)

    _server_thread = threading.Thread(target=_uvicorn_server.run, daemon=True)
    _server_thread.start()

    with console.status("[bold bright_yellow]  Starting prediction engine...[/]", spinner="dots"):
        for _ in range(40):
            time.sleep(0.5)
            if is_server_running():
                console.print("  [bold green]✔ Prediction engine is online![/]\n")
                return True

    console.print("  [bold red]✖ Server timed out.[/]\n")
    return False


def stop_server():
    global _uvicorn_server
    if _uvicorn_server:
        _uvicorn_server.should_exit = True


atexit.register(stop_server)


# ═════════════════════════════════════════════════════════════════════════
#   INPUT COLLECTION
# ═════════════════════════════════════════════════════════════════════════

MATERIALS = ["Aluminum", "Copper", "Steel", "Zinc", "Nickel", "Titanium", "Lead", "Tin"]
ROUTES = ["Primary", "Secondary"]
EOL_ROUTES = ["Recycled", "Landfill", "Incineration", "Reuse"]
TRANSPORT_MODES = ["Truck", "Rail", "Ship", "Truck+Ship", "Rail+Ship", "Air"]

NUMERIC_FIELDS = [
    # (key, display_name, unit, default, min, max)
    ("mining_energy_MJ_per_kg",           "Mining Energy",          "MJ/kg",  5.0,   0.0, 100.0),
    ("smelting_energy_MJ_per_kg",         "Smelting Energy",        "MJ/kg", 10.0,   0.0, 200.0),
    ("refining_energy_MJ_per_kg",         "Refining Energy",        "MJ/kg",  5.0,   0.0, 100.0),
    ("fabrication_energy_MJ_per_kg",      "Fabrication Energy",     "MJ/kg",  3.0,   0.0,  50.0),
    ("recycled_content_frac",             "Recycled Content",       "frac",   0.2,   0.0,   1.0),
    ("recycling_efficiency_frac",         "Recycling Efficiency",   "frac",   0.5,   0.0,   1.0),
    ("recycled_output_kg_per_kg",         "Recycled Output",        "kg/kg",  0.3,   0.0,   1.0),
    ("loop_closing_potential_USD_per_kg", "Loop Closing Potential", "$/kg",   0.1,   0.0,  10.0),
    ("reuse_potential_score",             "Reuse Potential",        "score",  0.5,   0.0,   1.0),
    ("repairability_score",               "Repairability",          "score",  0.5,   0.0,   1.0),
    ("product_lifetime_years",            "Product Lifetime",       "years", 10.0,   0.1,  50.0),
    ("transport_distance_km",             "Transport Distance",     "km",   500.0,   0.0, 20000.0),
    ("electricity_grid_renewable_pct",    "Grid Renewable Share",   "%",     40.0,   0.0, 100.0),
    ("renewable_electricity_frac",        "Renewable Electricity",  "frac",   0.4,   0.0,   1.0),
    ("material_criticality_score",        "Material Criticality",   "score",  0.3,   0.0,   1.0),
]


def choose_option(label, options, default_idx=0):
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
        console.print("    [red]Invalid, try again.[/]")


def get_numeric(display_name, unit, default, min_val, max_val):
    hint = f"[dim]{min_val}–{max_val} {unit}[/]"
    while True:
        try:
            val = FloatPrompt.ask(f"    [bright_cyan]{display_name}[/] {hint}", default=default)
            if min_val <= val <= max_val:
                return val
            console.print(f"    [red]Out of range ({min_val}–{max_val}).[/]")
        except Exception:
            console.print("    [red]Enter a valid number.[/]")


def collect_inputs():
    payload = {}

    # ── Section 1: Material Identity ──────────────────────────────
    console.print(Panel(
        "[bold]Select the material and its production route.[/]\n"
        "[dim]Primary = from ore  •  Secondary = from recycled scrap[/]",
        title="[bold bright_cyan]① Material Identity[/]",
        border_style="bright_cyan", box=box.ROUNDED, padding=(0, 2),
    ))
    console.print()
    payload["material"] = choose_option("Material Type", MATERIALS)
    payload["route"] = choose_option("Production Route", ROUTES)

    # ── Section 2: Energy Profile ─────────────────────────────────
    console.print(Panel(
        "[bold]Energy consumed at each stage of production.[/]\n"
        "[dim]All values in MJ per kg of final product.[/]",
        title="[bold bright_yellow]② Energy Profile[/]",
        border_style="bright_yellow", box=box.ROUNDED, padding=(0, 2),
    ))
    console.print()
    for key, name, unit, default, mn, mx in NUMERIC_FIELDS[:4]:
        payload[key] = get_numeric(name, unit, default, mn, mx)
    console.print()

    # ── Section 3: Circularity Metrics ────────────────────────────
    console.print(Panel(
        "[bold]Circular economy indicators for the material lifecycle.[/]\n"
        "[dim]Fractions range from 0 (none) to 1 (maximum).[/]",
        title="[bold bright_green]③ Circularity Metrics[/]",
        border_style="bright_green", box=box.ROUNDED, padding=(0, 2),
    ))
    console.print()
    for key, name, unit, default, mn, mx in NUMERIC_FIELDS[4:11]:
        payload[key] = get_numeric(name, unit, default, mn, mx)
    console.print()

    # ── Section 4: End-of-Life & Transport ────────────────────────
    console.print(Panel(
        "[bold]What happens after the product's useful life, and how it's transported.[/]\n"
        "[dim]Transport mode and distance affect the overall carbon footprint.[/]",
        title="[bold bright_magenta]④ End-of-Life & Transport[/]",
        border_style="bright_magenta", box=box.ROUNDED, padding=(0, 2),
    ))
    console.print()
    payload["end_of_life_route"] = choose_option("End-of-Life Route", EOL_ROUTES)
    _, name, unit, default, mn, mx = NUMERIC_FIELDS[11]
    payload["transport_distance_km"] = get_numeric(name, unit, default, mn, mx)
    payload["transport_mode"] = choose_option("Transport Mode", TRANSPORT_MODES)
    console.print()

    # ── Section 5: Grid & Criticality ─────────────────────────────
    console.print(Panel(
        "[bold]Electricity grid composition and raw material supply risk.[/]\n"
        "[dim]Higher renewable % = lower emissions  •  Higher criticality = supply risk.[/]",
        title="[bold bright_red]⑤ Grid & Material Criticality[/]",
        border_style="bright_red", box=box.ROUNDED, padding=(0, 2),
    ))
    console.print()
    for key, name, unit, default, mn, mx in NUMERIC_FIELDS[12:]:
        payload[key] = get_numeric(name, unit, default, mn, mx)
    console.print()

    return payload


def display_input_summary(payload):
    table = Table(
        title="📋 Input Summary",
        box=box.ROUNDED, border_style="bright_cyan",
        title_style="bold bright_white", show_lines=True, padding=(0, 1),
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


# ═════════════════════════════════════════════════════════════════════════
#   PREDICTION DISPLAY
# ═════════════════════════════════════════════════════════════════════════

def display_prediction(result, latency_ms):
    data = result["data"]["predictions"]
    mci = data["MCI_score"]
    emissions = data["emissions_kgCO2e"]
    material = result["data"]["input_material"]

    # ── MCI Assessment ────────────────────────────────────────────
    if mci > 0.7:
        mci_style, mci_label = "bold bright_green", "● HIGHLY CIRCULAR"
        mci_desc = "Excellent material circularity — strong recycling loop."
    elif mci > 0.3:
        mci_style, mci_label = "bold bright_yellow", "● TRANSITIONAL"
        mci_desc = "Moderate circularity — room for improvement in recycling."
    else:
        mci_style, mci_label = "bold bright_red", "● LINEAR (WASTE-PRONE)"
        mci_desc = "Low circularity — material is mostly wasted after use."

    # ── Emissions Assessment ──────────────────────────────────────
    if emissions < 2.0:
        emi_style, emi_label = "bold bright_green", "● LOW IMPACT"
        emi_desc = "Emissions within sustainable production thresholds."
    elif emissions < 5.0:
        emi_style, emi_label = "bold bright_yellow", "● MODERATE IMPACT"
        emi_desc = "Emissions are notable — consider process optimization."
    else:
        emi_style, emi_label = "bold bright_red", "● CRITICAL EMISSIONS"
        emi_desc = "High emissions — urgent decarbonization needed."

    # ── Results table ─────────────────────────────────────────────
    t = Table(box=box.HEAVY_EDGE, border_style="bright_blue", show_header=True,
              header_style="bold bright_magenta", padding=(0, 2))
    t.add_column("Metric", style="bright_cyan", min_width=22)
    t.add_column("Value", justify="right", style="bold bright_white", min_width=16)
    t.add_column("Assessment", justify="center", min_width=24)

    t.add_row("MCI Score",     f"{mci:.4f}",              Text(mci_label, style=mci_style))
    t.add_row("CO₂ Emissions", f"{emissions:.4f} kg/kg",  Text(emi_label, style=emi_style))
    t.add_row("API Latency",   f"{latency_ms:.0f} ms",    Text("⚡ Live", style="bold bright_cyan"))
    t.add_row("Transaction",   result["transaction_id"],   Text("✔ Logged", style="dim"))

    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    console.print(Panel(
        t,
        title=f"[bold bright_white]⬡  PREDICTION RESULT  ⬡[/]  [dim]│[/]  [bold bright_cyan]{material}[/]  [dim]│[/]  [dim]{ts}[/]",
        border_style="bright_blue", box=box.DOUBLE_EDGE, padding=(1, 2),
    ))

    # ── Interpretation ────────────────────────────────────────────
    interp = Text()
    interp.append("  Material Circularity:  ", style="bold")
    interp.append(f"{mci_desc}\n", style=mci_style.replace("bold ", ""))
    interp.append("  Environmental Impact:  ", style="bold")
    interp.append(f"{emi_desc}", style=emi_style.replace("bold ", ""))

    console.print(Panel(
        interp, title="[dim]Interpretation[/]",
        border_style="dim", box=box.ROUNDED, padding=(0, 2),
    ))
    console.print()


def send_prediction(payload):
    console.print()
    with console.status("[bold bright_yellow]  Running AI prediction...[/]", spinner="dots"):
        try:
            start = time.perf_counter()
            response = requests.post(PREDICT_URL, json=payload, timeout=15)
            latency = (time.perf_counter() - start) * 1000
        except requests.exceptions.ConnectionError:
            console.print(Panel(
                "[bold red]Could not connect to the prediction engine.[/]\n"
                "[dim]Please restart the application.[/]",
                title="[bold red]✖ Connection Failed[/]",
                border_style="red", box=box.DOUBLE_EDGE,
            ))
            return
        except requests.exceptions.Timeout:
            console.print(Panel("[bold red]Request timed out.[/]",
                                title="[bold red]✖ Timeout[/]", border_style="red"))
            return

    if response.status_code == 200:
        display_prediction(response.json(), latency)
    else:
        console.print(Panel(
            f"[bold red]HTTP {response.status_code}[/]\n{response.text}",
            title="[bold red]✖ Prediction Error[/]", border_style="red",
        ))


# ═════════════════════════════════════════════════════════════════════════
#   MAIN APPLICATION FLOW
# ═════════════════════════════════════════════════════════════════════════

def main():
    show_splash()

    # ── Step 1: Auto-start the prediction engine ──────────────────
    if not start_server():
        console.print(Panel(
            "[bold red]The prediction engine could not start.[/]\n\n"
            "[dim]Possible causes:[/]\n"
            "  • Model not trained yet — run: [bright_cyan]python -m src.train_model[/]\n"
            "  • Port 8000 is already in use\n"
            "  • Missing dependencies — run: [bright_cyan]pip install -r requirements.txt[/]",
            title="[bold red]✖ Startup Failed[/]",
            border_style="red", box=box.DOUBLE_EDGE, padding=(1, 2),
        ))
        return

    # ── Step 2: Prediction loop ───────────────────────────────────
    while True:
        try:
            console.print(Rule("[bold bright_cyan]Enter Material Data[/]", style="bright_cyan"))
            console.print()

            payload = collect_inputs()
            display_input_summary(payload)

            confirm = Prompt.ask(
                "  [bold bright_yellow]Run prediction?[/]",
                choices=["y", "n"], default="y",
            )

            if confirm == "y":
                send_prediction(payload)
            else:
                console.print("  [dim]Cancelled.[/]\n")

            again = Prompt.ask(
                "  [bold bright_cyan]Assess another material?[/]",
                choices=["y", "n"], default="y",
            )
            if again != "y":
                break

            console.print()
        except KeyboardInterrupt:
            console.print("\n")
            break

    # ── Shutdown ──────────────────────────────────────────────────
    console.print()
    with console.status("[bold bright_yellow]  Shutting down...[/]", spinner="dots"):
        stop_server()
        time.sleep(0.3)

    console.print(Panel(
        "[bright_cyan]Thank you for using LCA Analytics.[/]\n"
        "[dim]Circular Economy • Sustainable Metallurgy • AI-Powered Insights[/]",
        border_style="bright_cyan", box=box.DOUBLE_EDGE, padding=(1, 3),
    ))


if __name__ == "__main__":
    main()

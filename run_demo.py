import requests
import time
from rich.console import Console

console = Console()
URL = "http://127.0.0.1:8000/api/v1/predict"

# Realistic scenarios with all 18 parameters matching the training data
test_cases = [
    {
        "material": "Aluminum",
        "route": "Secondary",
        "mining_energy_MJ_per_kg": 2.1,
        "smelting_energy_MJ_per_kg": 4.5,
        "refining_energy_MJ_per_kg": 3.0,
        "fabrication_energy_MJ_per_kg": 2.5,
        "recycled_content_frac": 0.85,
        "recycling_efficiency_frac": 0.90,
        "recycled_output_kg_per_kg": 0.765,
        "loop_closing_potential_USD_per_kg": 0.15,
        "reuse_potential_score": 0.8,
        "repairability_score": 0.7,
        "product_lifetime_years": 15.0,
        "end_of_life_route": "Recycled",
        "transport_distance_km": 150.0,
        "transport_mode": "Rail",
        "electricity_grid_renewable_pct": 60.0,
        "renewable_electricity_frac": 0.6,
        "material_criticality_score": 0.2
    },
    {
        "material": "Copper",
        "route": "Primary",
        "mining_energy_MJ_per_kg": 8.5,
        "smelting_energy_MJ_per_kg": 15.0,
        "refining_energy_MJ_per_kg": 8.0,
        "fabrication_energy_MJ_per_kg": 4.0,
        "recycled_content_frac": 0.10,
        "recycling_efficiency_frac": 0.30,
        "recycled_output_kg_per_kg": 0.03,
        "loop_closing_potential_USD_per_kg": 0.05,
        "reuse_potential_score": 0.4,
        "repairability_score": 0.3,
        "product_lifetime_years": 5.0,
        "end_of_life_route": "Landfill",
        "transport_distance_km": 2000.0,
        "transport_mode": "Truck",
        "electricity_grid_renewable_pct": 20.0,
        "renewable_electricity_frac": 0.2,
        "material_criticality_score": 0.6
    }
]

def run_simulation():
    console.print("\n[bold cyan]--- STARTING LIVE API SIMULATION FOR REVIEW PANEL ---[/]\n")
    
    for i, payload in enumerate(test_cases):
        console.print(f"[yellow]Sending Scenario {i+1}: {payload['material']}...[/]")
        try:
            response = requests.post(URL, json=payload)
            if response.status_code == 200:
                console.print(f"[green]✔ Success![/] Received HTTP 200.")
            else:
                console.print(f"[red]✖ Error {response.status_code}:[/] {response.text}")
        except requests.exceptions.ConnectionError:
            console.print("[bold red]CRITICAL ERROR:[/] Could not connect to API. Is app.py running?")
            break
        
        time.sleep(2) # Pause for dramatic effect during the presentation
        
    console.print("\n[bold cyan]--- SIMULATION COMPLETE ---[/]\n")

if __name__ == "__main__":
    run_simulation()
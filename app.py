from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.core.inference import model_handler
from src.utils.logger import log_inference_dashboard
import time
import uvicorn

app = FastAPI(title="Metallurgy LCA API", version="1.0.0")

# Security & Validation: 19 Features matching the trained model exactly
class MaterialInput(BaseModel):
    material: str
    route: str
    mining_energy_MJ_per_kg: float
    smelting_energy_MJ_per_kg: float
    refining_energy_MJ_per_kg: float
    fabrication_energy_MJ_per_kg: float
    recycled_content_frac: float
    recycling_efficiency_frac: float
    recycled_output_kg_per_kg: float  # Added this missing feature
    loop_closing_potential_USD_per_kg: float
    reuse_potential_score: float
    repairability_score: float
    product_lifetime_years: float
    end_of_life_route: str
    transport_distance_km: float
    transport_mode: str
    electricity_grid_renewable_pct: float
    renewable_electricity_frac: float
    material_criticality_score: float

@app.get("/")
def health_check():
    return {"status": "online", "message": "Backend LCA Analytics Engine is active"}

@app.post("/api/v1/predict")
async def get_prediction(data: MaterialInput):
    try:
        features = data.model_dump()
        
        # The model_handler expects these exact features to make a prediction
        results = model_handler.predict(features)
        
        # Trigger the terminal UI in the server console
        log_inference_dashboard(results['mci'], results['emissions'], results['latency'])
        
        return {
            "status": "success",
            "transaction_id": "tx_req_" + str(int(time.time())),
            "data": {
                "input_material": data.material,
                "predictions": {
                    "MCI_score": results['mci'],
                    "emissions_kgCO2e": results['emissions']
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Added server startup block
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
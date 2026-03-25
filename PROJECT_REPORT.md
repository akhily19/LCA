# 📊 Metallurgy Life Cycle Assessment (LCA) — Project Report & Demo Guide

This report provides an overview of the LCA Analytics Engine and a step-by-step demonstration guide using guaranteed-to-work dummy inputs.

---

## 1. System Architecture

The project is structured into a cohesive pipeline that guarantees zero data leakage while providing real-time AI predictions:
* **The AI Engine** (`src.train_model`): Trains a `RandomForestRegressor` on 19 essential features to predict **MCI Score** and **Emissions (kg CO₂e)**.
* **The REST API** (`app.py`): A high-performance FastAPI server utilizing strictly defined Pydantic constraints.
* **The Unified Launcher** (`main.py`): A beautiful terminal UI using `Rich` that automatically starts the underlying server on a background daemon thread and provides an interactive terminal interface.

---

## 2. Demonstration Guide (Dummy Inputs)

When presenting this project or getting a feel for the application, use the following scenario.

### Scenario: Secondary Aluminum Production vs Primary Copper

Start the application by running:
```bash
python main.py
```

### Test Case A: Highly Circular, Low Emission (Secondary Aluminum)
This scenario demonstrates what a good, sustainable material profile looks like.

**① Material Identity**
*   **Material Type:** `1` *(Aluminum)*
*   **Production Route:** `2` *(Secondary)*

**② Energy Profile (MJ/kg)**
*   **Mining Energy:** `2.1`
*   **Smelting Energy:** `4.5`
*   **Refining Energy:** `3.0`
*   **Fabrication Energy:** `2.5`

**③ Circularity Metrics (Fractions/Scores)**
*   **Recycled Content:** `0.85`
*   **Recycling Efficiency:** `0.90`
*   **Recycled Output:** `0.765`
*   **Loop Closing Potential ($/kg):** `0.15`
*   **Reuse Potential:** `0.8`
*   **Repairability:** `0.7`
*   **Product Lifetime (years):** `15.0`

**④ End-of-Life & Transport**
*   **End-of-Life Route:** `1` *(Recycled)*
*   **Transport Distance (km):** `150.0`
*   **Transport Mode:** `2` *(Rail)*

**⑤ Grid & Material Criticality**
*   **Grid Renewable Share (%):** `60.0`
*   **Renewable Electricity (Frac):** `0.6`
*   **Material Criticality:** `0.2`

> **Expected Outcome:**
> *   **MCI Score:** ~0.65 *(TRANSITIONAL / HIGHLY CIRCULAR)*
> *   **CO₂ Emissions:** ~3.79 kg/kg *(MODERATE IMPACT)*

---

### Test Case B: Linear, High Emission (Primary Copper)
This scenario demonstrates a highly unsustainable profile.

**① Material Identity**
*   **Material Type:** `2` *(Copper)*
*   **Production Route:** `1` *(Primary)*

**② Energy Profile (MJ/kg)**
*   **Mining Energy:** `8.5`
*   **Smelting Energy:** `15.0`
*   **Refining Energy:** `8.0`
*   **Fabrication Energy:** `4.0`

**③ Circularity Metrics (Fractions/Scores)**
*   **Recycled Content:** `0.10`
*   **Recycling Efficiency:** `0.30`
*   **Recycled Output:** `0.03`
*   **Loop Closing Potential ($/kg):** `0.05`
*   **Reuse Potential:** `0.4`
*   **Repairability:** `0.3`
*   **Product Lifetime (years):** `5.0`

**④ End-of-Life & Transport**
*   **End-of-Life Route:** `2` *(Landfill)*
*   **Transport Distance (km):** `2000.0`
*   **Transport Mode:** `1` *(Truck)*

**⑤ Grid & Material Criticality**
*   **Grid Renewable Share (%):** `20.0`
*   **Renewable Electricity (Frac):** `0.2`
*   **Material Criticality:** `0.6`

> **Expected Outcome:**
> *   **MCI Score:** ~0.00 *(LINEAR / WASTE-PRONE)*
> *   **CO₂ Emissions:** Significantly higher than Aluminum.

---

## 3. Review of Bug Fixes & Project Health 

As part of finalizing this platform, the following critical issues were resolved:
1.  **Data Leakage Bug:** The initial model was inadvertently trained on exactly the variables it was supposed to predict (like `F`, `W_C`). This resulted in an HTTP 500 error when the API couldn't map user inputs to those targets. The model is now cleanly trained on 19 strictly exogenous features.
2.  **Schema Mismatches:** Corrected FastAPI Pydantic schemas (adding fields like `recycled_output_kg_per_kg`) to match the trained Random Forest precisely.
3.  **Port Conflicts / Pycache Issues:** Rewrote the unified launcher (`main.py`) to properly execute the `uvicorn` server inside a Daemon thread, entirely bypassing subprocess zombie states and Pycache conflicts.
4.  **Deprecated Pydantic Calls:** Migrated FastAPI response serializers from `.dict()` to `.model_dump()`.

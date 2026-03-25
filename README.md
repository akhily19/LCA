# 🌍 Metallurgy Life Cycle Assessment (LCA) Analytics Engine

An end-to-end framework for predicting environmental impacts (CO₂ emissions) and Material Circularity Indicators (MCI) for metals. This tool uses a machine learning model integrated with a Fast API backend and a professional terminal user interface to help engineers and researchers transition from linear to circular economies.

## ✨ Features

- **Predictive AI Modeling**: Utilizes an optimized Random Forest Regressor to predict highly non-linear relationships in metallurgy datasets.
- **RESTful API Backend**: High-performance FastAPI server (`app.py`) built with strictly validated Pydantic models.
- **Interactive Terminal UI**: A beautiful, menu-driven CLI experience (`main.py`) powered by `Rich` that automatically orchestrates the server and inputs.
- **Circularity Focus**: Outputs critical metrics like MCI Score and kg CO₂ equivalent per kg of material produced.

## 🚀 QuickStart

1. **Install Dependencies**
   It's highly recommended to use a virtual environment.
   ```bash
   pip install -r requirements.txt
   ```

2. **Train the Model (If not already trained)**
   *The repository might not include the 100MB+ model file.*
   ```bash
   python -m src.train_model
   ```

3. **Run the Application**
   Everything you need is wrapped inside the unified launcher. It will automatically start the lightweight API server in the background and walk you through a user-friendly data entry process.
   ```bash
   python main.py
   ```

## 🧠 Project Architecture

* `main.py`: The unified entry point. Contains the interactive UI and manages background threads for the FastAPI server.
* `app.py`: The FastAPI application defining the routes (`/api/v1/predict`) and input data validation schemas.
* `src/train_model.py`: The machine learning training pipeline. Reads from data, preprocesses features, trains the Random Forest, and serializes it to `models/`.
* `src/core/inference.py`: The wrapper module used by the API to load the `.pkl` model and handle prediction requests safely.
* `src/config.py`: Centralized configuration for directory paths to ensure the project works anywhere.

## 📝 Input Parameters

The tool takes 19 parameters categorised into:
1. **Material Identity**: Material type (Aluminum, Steel, etc.) & Route (Primary/Secondary).
2. **Energy Profile**: Energy used during Mining, Smelting, Refining, etc.
3. **Circularity Metrics**: Recycled Content, Recycling Efficiency, Product Lifetime.
4. **End-of-Life & Transport**: EOL Route, Transport Distance, and Transport Mode.
5. **Grid & Criticality**: Grid Renewable Share and Material Criticality.

## 🧪 Dummy Example Inputs by Material

To quickly test the application, you can use the following dummy profiles for each material type to see how the prediction engine evaluates different inputs. Leave all unspecified fields as their default values in the CLI.

| Material | Route | Mining Energy | Smelting Energy | Recycled Content | Recycling Efficiency | Product Lifetime | Expected Outcome |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Aluminum** | Secondary | 2.1 MJ/kg | 4.5 MJ/kg | 0.85 | 0.90 | 15.0 years | Highly Circular, Low Emissions |
| **Copper** | Primary | 8.5 MJ/kg | 15.0 MJ/kg | 0.10 | 0.30 | 5.0 years | Linear, High Emissions |
| **Steel** | Secondary | 3.0 MJ/kg | 7.0 MJ/kg | 0.70 | 0.85 | 30.0 years | Highly Circular, Low Emissions |
| **Zinc** | Primary | 6.0 MJ/kg | 12.0 MJ/kg | 0.15 | 0.25 | 10.0 years | Linear, Moderate Emissions |
| **Nickel** | Primary | 15.0 MJ/kg | 25.0 MJ/kg | 0.05 | 0.20 | 8.0 years | Linear, High Emissions |
| **Titanium** | Primary | 45.0 MJ/kg | 70.0 MJ/kg | 0.02 | 0.10 | 20.0 years | Linear, Extreme Emissions |
| **Lead** | Secondary | 1.5 MJ/kg | 3.5 MJ/kg | 0.95 | 0.95 | 3.0 years | Highly Circular, Low Emissions |
| **Tin** | Primary | 10.0 MJ/kg | 18.0 MJ/kg | 0.10 | 0.20 | 4.0 years | Linear, Moderate Emissions |

## 🛡️ Best Practices Applied

- Strict separation of concerns (Training vs. Inference vs. UI).
- Robust error handling for Server Timeouts and Validation Failures.
- Zero Data Leakage (Target-derived columns were strictly eliminated from the training feature set).
- Complete Path Safety via `pathlib` and centralized configs.

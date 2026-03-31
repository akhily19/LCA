# 🌍 Metallurgy Life Cycle Assessment (LCA) Analytics Engine
**Comprehensive Project Report & Presentation Guide**

---

## 1. Problem Statement
The metallurgical industry is one of the largest contributors to global carbon emissions. As the world shifts from a **Linear Economy** (take, make, dispose) to a **Circular Economy** (recycle, reuse, repair), engineers and policymakers need to measure the environmental impact of metal production precisely. 

However, calculating the **Material Circularity Indicator (MCI)** and the total **CO₂ equivalent emissions** for various metals is highly complex and non-linear. It involves analyzing dozens of variables across a material's entire lifespan—from mining energy and grid composition to product lifetime and end-of-life recycling. Traditional LCA methods are often slow, manual, and difficult to parameterize for rapid "what-if" scenario testing.

## 2. Project Solution
This project introduces the **LCA Analytics Engine**, an end-to-end framework that uses Machine Learning to predict environmental impacts and material circularity instantly. 

Instead of manual spreadsheet calculations, users input 19 key parameters into a beautifully designed, intuitive Interactive Terminal Interface. The system securely sends this data to a high-performance backend API, which queries a trained AI model, returning instantaneous assessments grading the sustainability of the process.

### Why is it Unique & Helpful?
1. **AI-Driven Assessment:** It uses a mathematical Random Forest algorithm that understands the highly non-linear relationships between variables (like how an increase in product lifetime interacts with grid renewable percentages) much better than simple formulas.
2. **Strict Quality Control (Zero Data Leakage):** The training pipeline rigorously excludes target-derived data, ensuring the model's predictions are genuine and unbiased.
3. **Consumer-Grade UI for Complex Data:** Instead of a complex web of scripts, it provides an interactive, menu-driven CLI (Command Line Interface). It prevents user errors by enforcing bounds (e.g., percentages between 0 and 1) and groups inputs logically.
4. **Instant API Microservice Architecture:** It sets the foundation for enterprise use. Because the core engine is an API, it can easily be connected to front-end web apps, mobile apps, or enterprise databases in the future.

---

## 3. Technology Stack (What It Uses)
The project is built entirely in Python, emphasizing robust data science and modern software engineering practices:

* **Machine Learning & Data Processing:** 
  * `scikit-learn`: For building the Random Forest Regressor and handling hyperparameter tuning (GridSearchCV).
  * `pandas` & `numpy`: For loading, sanitizing, and structuring the LCA datasets.
  * `joblib`: For serializing (saving/loading) the trained AI model efficiently.
* **Backend Server (REST API):**
  * `FastAPI`: An ultra-fast, modern web framework for building the API endpoints.
  * `Uvicorn`: An asynchronous server that runs the FastAPI application.
  * `Pydantic`: Ensures data validation (making sure a user sends a float instead of a string).
* **Frontend User Interface (CLI):**
  * `Rich`: A Python library that creates beautiful, color-coded, and cleanly formatted terminal outputs, progress bars, and data tables.
  * `requests`: For communicating from the CLI to the local API backend.

---

## 4. How It Works (Project Architecture)

The project follows a clean separation of concerns:

### Step 1: Model Training (`src/train_model.py`)
The system ingests a dataset of 5,000+ metallurgical scenarios for various metals (Aluminum, Copper, Steel, etc.). It filters out invalid data, isolates 19 crucial features, and trains a `MultiOutputRegressor(RandomForestRegressor)`. The best version of the model is saved entirely to a `.pkl` file.

### Step 2: The API Backend (`app.py` & `src/core/inference.py`)
When `app.py` is executed, it loads the saved model into RAM. It exposes a single route: `/api/v1/predict`. When it receives data, it verifies it, hands it down to the `inference.py` engine, and the model calculates the exact MCI score and CO₂ emissions, returning a JSON response.

### Step 3: The Unified Launcher & UI (`main.py`)
This is the heart of the user experience. When a user runs `main.py`:
1. It automatically spins up the `app.py` server in a background daemon thread so the user doesn't have to start it manually.
2. It prompts the user for 19 specific inputs grouped into 5 categories (Material Identity, Energy Profile, Circularity Metrics, End-of-Life, Grid Criticality).
3. It packages these answers into a JSON format, fires it to the API, and then visually parses the results, color-coding the output (e.g., Green for "Highly Circular", Red for "Critical Emissions").

---

## 5. Sample Supervisor Questions (Q&A Prep)

Use these questions to prepare yourself to defend the project confidently.

> **Q1: Why did you choose a Random Forest model instead of simple Linear Regression?**  
> **A:** Metallurgical impacts are highly non-linear. The interaction between variables—like *Transport Distance* and *Transport Mode* compared against *Grid Renewable Share*—creates complex decision boundaries. Random Forest handles these non-linear interactions excellently and is highly resistant to overfitting, especially when optimized using cross-validation (GridSearchCV).

> **Q2: I see you mentioned "Zero Data Leakage" in the project. What does that mean and how did you do it?**  
> **A:** Data Leakage happens when the model accidentally has access to the "answer" during training. In our dataset, there are columns like `MCI_raw`, `W_kg` (waste), and `recovered_kg` which are mathematically directly related to the final score. In our pipeline (`train_model.py`), I explicitly programmed the system to drop all intermediate and target-derived columns before training, forcing the AI to successfully learn from true initial parameters.

> **Q3: Why separate the system into a Frontend UI and a Backend API instead of just calculating it in one script?**  
> **A:** It’s about scalability and modern software architecture. By decoupling the AI logic into a standalone REST API (FastAPI), we can interact with the engine from anywhere. Right now we use a Python Terminal UI, but tomorrow we could plug a React website or an iOS app into the exact same API without rewriting any of our Machine Learning code.

> **Q4: What exactly is the MCI Score that your tool predicts?**  
> **A:** The Material Circularity Indicator (MCI) is a value between 0 and 1. A score of 0 denotes a perfectly linear model (take resources, use them, throw them in a landfill). A score of 1 denotes a perfectly circular system (100% recycled or reused, zero waste). It allows companies to put a quantifiable metric on their sustainability goals.

> **Q5: How does your application handle communication between the terminal interface and the ML model?**  
> **A:** The `main.py` script utilizes Python threading to quietly deploy a Uvicorn server in the background on port `8000`. The script then uses the `requests` library to trigger standard HTTP POST requests to the API, exactly as an internet browser or modern web service would.

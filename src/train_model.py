import pandas as pd
import numpy as np
import joblib
import os
import time
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from rich.console import Console
from rich.panel import Panel

from src.config import RAW_DATA_PATH, MODEL_SAVE_PATH

console = Console()


def load_and_preprocess_data(file_path):
    if not os.path.exists(file_path):
        console.print(f"[bold red]CRITICAL ERROR:[/] {file_path} not found.")
        exit(1)

    df = pd.read_csv(file_path)

    # 1. DEFINE TARGETS (What we are predicting)
    targets = ['emissions_kgCO2e_per_kg', 'MCI']
    
    # 2. ANTI-DATA LEAKAGE: Drop columns the model shouldn't see during training
    #    This includes targets, aggregated energy, MCI intermediates, and metadata
    drop_cols = targets + [
        'energy_MJ_per_kg', 'V_kg', 'recovered_kg', 'W_kg',
        'year', 'country', 'missing_data_flag',
        'MCI_raw', 'MCI_percent', 'LFI', 'F',
        'lifespan_clipped', 'circularity_index_default',
        'economic_value_USD_per_kg'
    ]
    
    cols_to_drop = [c for c in drop_cols if c in df.columns]
    
    X = df.drop(columns=cols_to_drop)
    y = df[targets]

    return X, y

def build_and_tune_pipeline(X_train, y_train):
    """
    Builds the pipeline and runs GridSearchCV to find the mathematical optimum.
    """
    numeric_features = X_train.select_dtypes(include=['int64', 'float64']).columns
    categorical_features = X_train.select_dtypes(include=['object']).columns

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ])

    rf_base = RandomForestRegressor(random_state=42)
    model = MultiOutputRegressor(rf_base)

    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', model)
    ])

    param_grid = {
        'regressor__estimator__n_estimators': [100, 200],
        'regressor__estimator__max_depth': [10, 20, None],
        'regressor__estimator__min_samples_split': [2, 5]
    }

    console.print("[bold cyan]Initializing GridSearchCV (3-Fold CV)[/]")
    console.print(f"Testing {len(param_grid['regressor__estimator__n_estimators']) * len(param_grid['regressor__estimator__max_depth']) * len(param_grid['regressor__estimator__min_samples_split'])} parameter combinations...")

    grid_search = GridSearchCV(
        pipeline, 
        param_grid, 
        cv=3,
        scoring='neg_mean_squared_error', 
        n_jobs=-1,
        verbose=1
    )

    start_time = time.time()
    grid_search.fit(X_train, y_train)
    training_time = round(time.time() - start_time, 2)

    console.print(f"[bold green]GridSearch Complete in {training_time} seconds.[/]")
    
    best_pipeline = grid_search.best_estimator_
    best_params = grid_search.best_params_

    return best_pipeline, best_params

def main():
    os.makedirs('models', exist_ok=True)
    console.print(Panel.fit("[bold white]LCA Model Training Pipeline (Production Grade)[/]", border_style="blue"))
    
    X, y = load_and_preprocess_data(RAW_DATA_PATH)
    console.print(f"[green]✔ Dataset loaded.[/] Features: {X.shape[1]}, Samples: {X.shape[0]}")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    with console.status("[bold yellow]Training and Tuning Model... Please wait.", spinner="dots"):
        best_pipeline, best_params = build_and_tune_pipeline(X_train, y_train)

    console.print("\n[bold magenta]🏆 Optimal Hyperparameters Found:[/]")
    for param, value in best_params.items():
        clean_param_name = param.replace('regressor__estimator__', '')
        console.print(f"   • {clean_param_name}: [bold yellow]{value}[/]")

    predictions = best_pipeline.predict(X_test)
    console.print("\n[bold cyan]📊 PRODUCTION PERFORMANCE METRICS[/]")
    
    for i, target in enumerate(y.columns):
        mae = mean_absolute_error(y_test.iloc[:, i], predictions[:, i])
        r2 = r2_score(y_test.iloc[:, i], predictions[:, i])
        
        r2_color = "green" if r2 > 0.8 else ("yellow" if r2 > 0.6 else "red")
        
        console.print(f"\n[bold underline]{target}[/]")
        console.print(f"   • Mean Absolute Error (MAE): {mae:.4f}")
        console.print(f"   • R² Score: [{r2_color}]{r2:.4f}[/]")

    joblib.dump(best_pipeline, MODEL_SAVE_PATH)
    console.print(f"\n[bold green]✔ Optimized Model successfully saved to {MODEL_SAVE_PATH}[/]")

if __name__ == "__main__":
    main()
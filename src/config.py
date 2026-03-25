import os

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- SYSTEM PATHS ---
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw", "LCA_multi_metal_with_MCI.csv")
PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "cleaned_lca_data.csv")

# Note: Changed to saved_models based on your directory tree
MODEL_SAVE_PATH = os.path.join(BASE_DIR, "models", "lca_model_v1.pkl")

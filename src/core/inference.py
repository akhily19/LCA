import time
import joblib
import pandas as pd
from src.config import MODEL_SAVE_PATH

class MLModelHandler:
    def __init__(self):
        self.model = None
        try:
            # We wrap this in a try-except block so the server doesn't crash 
            # if you forget to train the model first.
            self.model = joblib.load(MODEL_SAVE_PATH)
            print(f"[SYSTEM] Model loaded successfully from {MODEL_SAVE_PATH}")
        except FileNotFoundError:
            print("[WARNING] Model file not found. Please run train_model.py first.")

    def predict(self, input_features: dict):
        start_time = time.perf_counter()
        
        if self.model is None:
            raise Exception("Model is not initialized. Cannot run inference.")

        # Convert the dictionary from FastAPI into a DataFrame for the model
        # We wrap it in a list to make it a 1-row 2D array, which sklearn requires
        df_input = pd.DataFrame([input_features])
        
        # Run actual inference
        predictions = self.model.predict(df_input)
        
        # Extract the multi-output predictions (assuming targets: ['emissions', 'MCI'])
        emissions = float(predictions[0][0])
        mci_score = float(predictions[0][1])
        
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        
        return {
            "mci": mci_score,
            "emissions": emissions,
            "latency": latency_ms
        }

# Initialize a single instance to be used across the whole app
model_handler = MLModelHandler()
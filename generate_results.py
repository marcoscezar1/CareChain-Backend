'''import json
import importlib.util
import pandas as pd
from enum import Enum

class Status(Enum):
    BELOW_EXPECTED = 0
    ABOVE_EXPECTED = 1
    WITHIN_EXPECTED = 2

def load_columns():
    with open("columns_metadata.json", "r") as f:
        columns_data = json.load(f)
    return columns_data["columns"]

def preprocess_input(input_json, columns):
    processed_data = pd.DataFrame()
    input_df = pd.DataFrame([input_json])

    input_df = pd.get_dummies(input_df)

    for col in columns:
        if col not in input_df:
            processed_data[col] = [0]
        else:
            processed_data[col] = input_df[col].values
    return processed_data.values[0]

def predict(model_path, input_json, target):
    columns = load_columns()
    columns.remove(target)
    input_data = preprocess_input(input_json, columns)

    spec = importlib.util.spec_from_file_location("model", model_path)
    model_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model_module)

    prediction = model_module.score(input_data)

    return prediction

def evaluate_prediction(target, predicted_value, real_value, tolerance_percent=10):
    error_margin = (tolerance_percent / 100) * predicted_value
    lower_bound = predicted_value - error_margin
    upper_bound = predicted_value + error_margin

    if real_value < lower_bound:
        status = Status.BELOW_EXPECTED
    elif real_value > upper_bound:
        status = Status.ABOVE_EXPECTED
    else:
        status = Status.WITHIN_EXPECTED

    return {
        "target": target,
        "predicted_value": round(predicted_value, 2),
        "real_value": real_value,
        "error_margin": round(error_margin, 2),
        "lower_bound": round(lower_bound, 2),
        "upper_bound": round(upper_bound, 2),
        "status": status
    }

targets = ["Avg_BPM", "Sleep_Hours", "Calories_Burned", "Water_Intake (liters)"]
'''
def generate_results(new_entry_json):
    return 4
        
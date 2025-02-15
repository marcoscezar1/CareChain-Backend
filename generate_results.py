import json
import importlib.util
from enum import Enum

class Status(Enum):
    BELOW_EXPECTED = 0
    ABOVE_EXPECTED = 1
    WITHIN_EXPECTED = 2

def load_columns():
    with open("columns_metadata.json", "r") as f:
        columns_data = json.load(f)
    return columns_data["columns"], columns_data["categorical_columns"]


def preprocess_input(input_json, columns, categorical_columns):
    processed_data = [0] * len(columns)
    for key, value in input_json.items():
        if key in categorical_columns:
            onehot_prefix = f"{key}_"
            onehot_key = onehot_prefix + str(value)

            if onehot_key in columns:
                index = columns.index(onehot_key)
                processed_data[index] = 1
        elif key in columns:
            index = columns.index(key)
            processed_data[index] = value

    return processed_data

def predict(model_path, input_json, target):
    columns, categorical_columns = load_columns()
    columns.remove(target)
    input_data = preprocess_input(input_json, columns, categorical_columns)

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
        status = Status.BELOW_EXPECTED.value
    elif real_value > upper_bound:
        status = Status.ABOVE_EXPECTED.value
    else:
        status = Status.WITHIN_EXPECTED.value

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



def generate_results(new_entry_json):
    new_entry = json.loads(new_entry_json)
    care_results = {}
    for target_to_predict in targets:
        real_value = new_entry[target_to_predict]

        model_path = f"model_{target_to_predict}.py"
        predicted_value = predict(model_path, new_entry, target_to_predict)

        result = evaluate_prediction(target_to_predict, predicted_value, real_value, tolerance_percent=10)
        care_results[target_to_predict] = result
    return json.dumps(care_results)



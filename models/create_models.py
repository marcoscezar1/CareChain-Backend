import pandas as pd
import m2cgen as m2c
import json
from sklearn.ensemble import RandomForestRegressor

df = pd.read_csv("dataset_com_sono.csv").dropna()

targets = ["Avg_BPM", "Sleep_Hours", "Calories_Burned", "Water_Intake (liters)"]

cols_to_remove = ["Workout_Frequency (days/week)", "Experience_Level", "BMI", "Fat_Percentage"]
df = df.drop(columns=cols_to_remove, errors='ignore')

categorical_columns = ["Gender", "Workout_Type"]

df = pd.get_dummies(df, columns=categorical_columns)

columns_metadata = {
    "columns": list(df.columns),
}
with open("columns_metadata.json", "w") as f:
    json.dump(columns_metadata, f)

best_params = {
    "Avg_BPM": {"bootstrap": True, "max_depth": 3, "min_samples_leaf": 4, "min_samples_split": 2, "n_estimators": 300},
    "Sleep_Hours": {"bootstrap": True, "max_depth": 3, "min_samples_leaf": 1, "min_samples_split": 10, "n_estimators": 100},
    "Calories_Burned": {"bootstrap": True, "max_depth": 3, "min_samples_leaf": 1, "min_samples_split": 5, "n_estimators": 300},
    "Water_Intake (liters)": {"bootstrap": True, "max_depth": 5, "min_samples_leaf": 2, "min_samples_split": 10, "n_estimators": 100},
}

for target in targets:
    train_set = df.drop(columns=[target])
    columns_list = list(train_set.columns)

    model = RandomForestRegressor(**best_params[target])
    model.fit(train_set, df[target])
    model_code = m2c.export_to_python(model)
    model_code = f"columns = {columns_list}\n\n" + model_code
    with open(f"model_{target}.py", "w") as f:
        f.write(model_code)

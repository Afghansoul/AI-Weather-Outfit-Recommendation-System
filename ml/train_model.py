import pandas as pd
import joblib

from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


# --------------------------------------------------
# PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).parent

DATASET_PATH = BASE_DIR / "dataset.csv"
MODEL_PATH = BASE_DIR / "outfit_model.pkl"


# --------------------------------------------------
# LOAD DATASET
# --------------------------------------------------

print("=" * 60)
print("LOADING DATASET")
print("=" * 60)

data = pd.read_csv(DATASET_PATH)

print(f"Dataset rows: {len(data)}")
print(f"Dataset columns: {len(data.columns)}")


# --------------------------------------------------
# FEATURES AND TARGET
# --------------------------------------------------

features = [
    "temperature",
    "humidity",
    "wind_speed",
    "rain",
    "season",
    "weather_condition",
    "occasion",
    "style"
]

target = "outfit_category"


X = data[features]
y = data[target]


# --------------------------------------------------
# TRAIN / TEST SPLIT
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print()
print(f"Training samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")


# --------------------------------------------------
# FEATURE TYPES
# --------------------------------------------------

numeric_features = [
    "temperature",
    "humidity",
    "wind_speed",
    "rain"
]

categorical_features = [
    "season",
    "weather_condition",
    "occasion",
    "style"
]


# --------------------------------------------------
# PREPROCESSING
# --------------------------------------------------

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        )
    ],
    remainder="passthrough"
)


# --------------------------------------------------
# RANDOM FOREST MODEL
# --------------------------------------------------

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    max_depth=12,
    min_samples_split=4,
    class_weight="balanced"
)


# --------------------------------------------------
# COMPLETE ML PIPELINE
# --------------------------------------------------

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)


# --------------------------------------------------
# TRAIN MODEL
# --------------------------------------------------

print()
print("=" * 60)
print("TRAINING RANDOM FOREST MODEL")
print("=" * 60)

pipeline.fit(
    X_train,
    y_train
)


# --------------------------------------------------
# PREDICTION
# --------------------------------------------------

y_pred = pipeline.predict(X_test)


# --------------------------------------------------
# ACCURACY
# --------------------------------------------------

accuracy = accuracy_score(
    y_test,
    y_pred
)

print()
print("=" * 60)
print("MODEL EVALUATION")
print("=" * 60)

print(
    f"Accuracy: {accuracy * 100:.2f}%"
)


# --------------------------------------------------
# CLASSIFICATION REPORT
# --------------------------------------------------

print()
print("Classification Report:")
print(
    classification_report(
        y_test,
        y_pred,
        zero_division=0
    )
)


# --------------------------------------------------
# CONFUSION MATRIX
# --------------------------------------------------

print()
print("Confusion Matrix:")

matrix = confusion_matrix(
    y_test,
    y_pred
)

print(matrix)


# --------------------------------------------------
# SAVE MODEL
# --------------------------------------------------

joblib.dump(
    pipeline,
    MODEL_PATH
)


# --------------------------------------------------
# FINAL INFORMATION
# --------------------------------------------------

print()
print("=" * 60)
print("MODEL TRAINING COMPLETED")
print("=" * 60)

print(f"Model saved to:")
print(MODEL_PATH)

print()
print("Model type: Random Forest Classifier")
print(f"Number of trees: {model.n_estimators}")
print(f"Accuracy: {accuracy * 100:.2f}%")

print("=" * 60)

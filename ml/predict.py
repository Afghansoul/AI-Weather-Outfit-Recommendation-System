import joblib
import pandas as pd
from pathlib import Path


# --------------------------------------------------
# MODEL PATH
# --------------------------------------------------

MODEL_PATH = Path(__file__).parent / "outfit_model.pkl"


# --------------------------------------------------
# LOAD MODEL
# --------------------------------------------------

model = joblib.load(MODEL_PATH)


# --------------------------------------------------
# PREDICTION FUNCTION
# --------------------------------------------------

def predict_outfit(
    temperature,
    humidity,
    wind_speed,
    rain,
    season,
    weather_condition,
    occasion,
    style
):
    """
    Predict the most suitable outfit category
    using the trained Random Forest model.
    """

    input_data = pd.DataFrame([
        {
            "temperature": temperature,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "rain": rain,
            "season": season,
            "weather_condition": weather_condition,
            "occasion": occasion,
            "style": style
        }
    ])

    prediction = model.predict(input_data)

    return prediction[0]


# --------------------------------------------------
# CONFIDENCE
# --------------------------------------------------

def get_prediction_confidence(
    temperature,
    humidity,
    wind_speed,
    rain,
    season,
    weather_condition,
    occasion,
    style
):
    """
    Return the predicted outfit and model confidence.
    """

    input_data = pd.DataFrame([
        {
            "temperature": temperature,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "rain": rain,
            "season": season,
            "weather_condition": weather_condition,
            "occasion": occasion,
            "style": style
        }
    ])

    prediction = model.predict(input_data)[0]

    probabilities = model.predict_proba(input_data)[0]

    confidence = max(probabilities) * 100

    return prediction, confidence

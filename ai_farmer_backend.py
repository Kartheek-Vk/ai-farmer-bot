"""Core backend logic for an AI Farmer Profit Optimization system."""

from __future__ import annotations
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "Crop_recommendation.csv"
MODEL_PATH = BASE_DIR / "crop_model.pkl"

# Dummy Data
crop_prices = {
    "rice": 2000,
    "maize": 1800,
    "cotton": 3000,
    "wheat": 2200,
}

crop_costs = {
    "rice": 1200,
    "maize": 1000,
    "cotton": 2000,
    "wheat": 1400,
}

DEFAULT_PRICE = 1500
DEFAULT_COST = 1000


# Simple trend factors for dummy price forecasting.
price_trend_factors = {
    "rice": 1.06,
    "maize": 0.97,
    "cotton": 1.08,
    "wheat": 1.03,
}


# ========================
# DATASET LOADING
# ========================
def load_dataset(file_path: Path = DATASET_PATH) -> pd.DataFrame:
    if not file_path.exists():
        raise FileNotFoundError("Dataset not found!")

    df = pd.read_csv(file_path)
    print("Dataset Loaded Successfully")
    print(df.head())
    return df


# ========================
# MODEL TRAINING
# ========================
def train_model():
    df = load_dataset()

    X = df[["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)

    print("Accuracy:", acc)

    joblib.dump(model, MODEL_PATH)
    print("Model saved")

    return model


# ========================
# PROFIT FUNCTION
# ========================
def calculate_profit(crop, price, cost):
    return price - cost


# ========================
# PRICE PREDICTION
# ========================
def predict_price(crop):
    """Predict a near-term selling price using a simple trend factor."""
    crop_name = str(crop).lower()
    base_price = crop_prices.get(crop_name, DEFAULT_PRICE)
    trend_factor = price_trend_factors.get(crop_name, 1.02)
    predicted_price = round(base_price * trend_factor, 2)
    return predicted_price


def get_selling_advice(current_price, predicted_price):
    """Suggest when to sell based on the predicted price trend."""
    if predicted_price > current_price:
        return "Wait 3-5 days before selling"
    return "Sell immediately for best profit"


def get_prediction_details(model, input_data):
    """Return the predicted crop, model confidence, and top class probabilities."""
    probabilities = model.predict_proba(input_data)[0]
    class_names = [str(class_name).lower() for class_name in model.classes_]

    probability_pairs = sorted(
        zip(class_names, probabilities),
        key=lambda item: item[1],
        reverse=True,
    )

    predicted_crop, top_probability = probability_pairs[0]
    top_probabilities = [
        {"crop": crop_name, "probability": round(probability * 100, 2)}
        for crop_name, probability in probability_pairs[:3]
    ]

    confidence = round(top_probability * 100, 2)
    return predicted_crop, confidence, top_probabilities


# ========================
# RISK ALERTS
# ========================
def get_risk_alerts(temp, humidity, rainfall):
    alerts = []

    if rainfall > 80:
        alerts.append("⚠️ Heavy rain expected")

    if humidity > 85:
        alerts.append("⚠️ High pest risk")

    if temp > 35:
        alerts.append("⚠️ Heat stress risk")

    if not alerts:
        alerts.append("✅ No major risks detected")

    return alerts


# ========================
# LOAD MODEL
# ========================
def load_model():
    if not MODEL_PATH.exists():
        return train_model()
    return joblib.load(MODEL_PATH)


# ========================
# DECISION FUNCTION (CORE)
# ========================
def decision_function(N, P, K, temp, humidity, ph, rainfall):

    model = load_model()

    input_data = pd.DataFrame(
        [[N, P, K, temp, humidity, ph, rainfall]],
        columns=["N", "P", "K", "temperature", "humidity", "ph", "rainfall"],
    )

    crop, confidence, top_probabilities = get_prediction_details(model, input_data)

    price = crop_prices.get(crop, DEFAULT_PRICE)
    predicted_price = predict_price(crop)
    cost = crop_costs.get(crop, DEFAULT_COST)

    profit = calculate_profit(crop, predicted_price, cost)

    alerts = get_risk_alerts(temp, humidity, rainfall)
    selling_advice = get_selling_advice(price, predicted_price)

    # 🔥 Improved Recommendation Logic
    if profit > 1500:
        message = " Highly profitable crop recommended"
    elif profit > 800:
        message = " Moderate profit crop"
    else:
        message = "Low profit - consider alternatives"

    #  Explainable AI (for research)
    if predicted_price > price:
        trend_reason = "market trend suggests a short-term price increase"
    else:
        trend_reason = "current market price is likely the best near-term selling window"

    reason = (
        f"{crop} selected based on soil conditions, model confidence {confidence:.2f}%, "
        f"expected profit ₹{profit}, and {trend_reason}."
    )

    return {
        "crop": crop,
        "confidence": confidence,
        "top_probabilities": top_probabilities,
        "price": price,
        "predicted_price": predicted_price,
        "cost": cost,
        "profit": profit,
        "alerts": alerts,
        "recommendation": message,
        "reason": reason,
        "selling_advice": selling_advice,
    }


# ========================
# TEST
# ========================
if __name__ == "__main__":
    result = decision_function(90, 40, 40, 25, 80, 6.5, 200)
    print(result)

import joblib
import pandas as pd


MODEL_PATH = "ml/models/baseline_model.pkl"

model = joblib.load(MODEL_PATH)


FEATURE_NAMES = [
    "amount",
    "has_sender",
    "has_receiver",
    "sender_transaction_count",
    "total_amount_sent",
    "unique_receiver_count",
    "recent_transaction_count"
]


def predict_fraud(features):
    feature_data = pd.DataFrame(
        [features],
        columns=FEATURE_NAMES
    )

    prediction = model.predict(feature_data)[0]
    probability = model.predict_proba(feature_data)[0][1]

    return {
        "prediction": int(prediction),
        "fraud_probability": float(probability)
    }
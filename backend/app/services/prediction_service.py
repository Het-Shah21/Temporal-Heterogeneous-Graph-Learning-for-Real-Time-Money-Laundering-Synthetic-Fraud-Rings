from backend.app.services.ml_contract import (
    ArtifactUnavailable,
    BASELINE_MODEL_PATH,
    FEATURE_NAMES,
)

MODEL_PATH = BASELINE_MODEL_PATH
model = None
ModelUnavailable = ArtifactUnavailable


def _load_model():
    global model
    if model is None:
        if not MODEL_PATH.exists():
            raise ModelUnavailable(f"Baseline XGBoost artifact not found: {MODEL_PATH}")
        try:
            import xgboost as xgb
            loaded_model = xgb.XGBClassifier()
            loaded_model.load_model(str(MODEL_PATH))
            model = loaded_model
        except Exception as error:
            raise ModelUnavailable("Baseline XGBoost artifact could not be loaded") from error
    return model


def predict_fraud(features):
    if len(features) != len(FEATURE_NAMES):
        raise ValueError(f"Expected {len(FEATURE_NAMES)} baseline features")
    loaded_model = _load_model()
    feature_data = [[float(value) for value in features]]

    prediction = loaded_model.predict(feature_data)[0]
    probability = loaded_model.predict_proba(feature_data)[0][1]

    return {
        "prediction": int(prediction),
        "fraud_probability": float(probability)
    }

import math
import pandas as pd

from backend.app.services.ml_contract import (
    ArtifactUnavailable,
    BASELINE_MODEL_PATH,
    FEATURE_NAMES,
    load_scaler,
)

MODEL_PATH = BASELINE_MODEL_PATH
model = None
ModelUnavailable = ArtifactUnavailable


def _load_xgboost_model():
    import xgboost as xgb
    loaded_model = xgb.XGBClassifier()
    loaded_model.load_model(str(MODEL_PATH))
    return loaded_model


def _validate_model_contract(loaded_model):
    feature_count = getattr(loaded_model, "n_features_in_", None)
    if feature_count is not None and feature_count != len(FEATURE_NAMES):
        raise ModelUnavailable("Baseline XGBoost model must expose seven input features")

    feature_names = getattr(loaded_model, "feature_names_in_", None)
    if feature_names is None:
        try:
            feature_names = loaded_model.get_booster().feature_names
        except AttributeError:
            feature_names = None

    if feature_names is not None and list(feature_names) != FEATURE_NAMES:
        raise ModelUnavailable(
            "Baseline XGBoost model feature names do not match the backend contract"
        )


def _load_model():
    global model
    if model is None:
        if not MODEL_PATH.exists():
            raise ModelUnavailable(f"Baseline XGBoost artifact not found: {MODEL_PATH}")
        try:
            load_scaler()
            loaded_model = _load_xgboost_model()
            _validate_model_contract(loaded_model)
            model = loaded_model
        except ModelUnavailable:
            raise
        except Exception as error:
            raise ModelUnavailable("Baseline XGBoost artifact could not be loaded") from error
    return model


def predict_fraud(features):
    if not isinstance(features, (list, tuple)) or len(features) != len(FEATURE_NAMES):
        raise ValueError(f"Expected {len(FEATURE_NAMES)} baseline features")

    numeric_features = []
    for value in features:
        if isinstance(value, bool):
            raise ValueError("Baseline features must be finite numeric values")
        try:
            numeric_value = float(value)
        except (TypeError, ValueError) as error:
            raise ValueError("Baseline features must be finite numeric values") from error
        if not math.isfinite(numeric_value):
            raise ValueError("Baseline features must be finite numeric values")
        numeric_features.append(numeric_value)

    loaded_model = _load_model()
    feature_data = pd.DataFrame([numeric_features], columns=FEATURE_NAMES)
    if feature_data.shape != (1, len(FEATURE_NAMES)):
        raise ValueError("Baseline inference input must have shape (1, 7)")

    prediction = loaded_model.predict(feature_data)[0]
    probabilities = loaded_model.predict_proba(feature_data)
    if getattr(probabilities, "shape", None) != (1, 2):
        raise ValueError("Baseline model returned an invalid probability shape")
    probability = float(probabilities[0][1])
    if not math.isfinite(probability) or not 0.0 <= probability <= 1.0:
        raise ValueError("Baseline model returned an invalid fraud probability")

    return {
        "prediction": int(prediction),
        "fraud_probability": float(probability)
    }

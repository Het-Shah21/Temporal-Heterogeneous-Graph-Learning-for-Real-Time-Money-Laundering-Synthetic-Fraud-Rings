from backend.app.services.feature_service import build_transaction_features
from backend.app.services.ml_contract import FEATURE_NAMES


def get_ml_feature_vector(transaction_id, sender_id):
    features = build_transaction_features(
        transaction_id,
        sender_id
    )

    if features is None:
        return None

    return [features[name] for name in FEATURE_NAMES]

from backend.app.services.feature_service import build_transaction_features


def get_ml_feature_vector(transaction_id, sender_id):
    features = build_transaction_features(
        transaction_id,
        sender_id
    )

    if features is None:
        return None

    return [
        features["amount"],
        features["has_sender"],
        features["has_receiver"],
        features["sender_transaction_count"],
        features["total_amount_sent"],
        features["unique_receiver_count"],
        features["recent_transaction_count"]
    ]
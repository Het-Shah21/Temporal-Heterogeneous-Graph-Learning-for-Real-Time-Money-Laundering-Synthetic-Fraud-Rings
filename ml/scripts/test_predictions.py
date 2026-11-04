from backend.app.services.prediction_service import predict_fraud


test_cases = {
    "normal": [
        1000.0,
        1,
        1,
        2,
        2000.0,
        1,
        1
    ],
    "suspicious": [
        75000.0,
        1,
        1,
        50,
        500000.0,
        30,
        40
    ]
}


for name, features in test_cases.items():
    result = predict_fraud(features)

    print(f"\n{name.upper()}")
    print(f"Prediction: {result['prediction']}")
    print(f"Fraud probability: {result['fraud_probability']:.2f}")
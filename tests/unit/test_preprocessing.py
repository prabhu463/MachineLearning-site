from ml.src.data_generation import generate_dataset
from ml.src.preprocessing import clean_data, engineer_features, impute_missing_values


def test_feature_engineering_adds_columns():
    frame = generate_dataset(20)
    cleaned = clean_data(frame)
    engineered = engineer_features(cleaned)
    imputed = impute_missing_values(engineered)
    assert "rolling_cpu_mean" in imputed.columns
    assert "latency_to_response_ratio" in imputed.columns

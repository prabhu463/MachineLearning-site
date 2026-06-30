from ml.src.data_generation import generate_dataset


def test_generate_dataset_shape():
    frame = generate_dataset(50)
    assert len(frame) == 50
    assert {"cpu_usage", "memory_usage", "incident_label"}.issubset(frame.columns)

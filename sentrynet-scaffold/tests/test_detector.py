import numpy as np
import pandas as pd
import pytest

from sentrynet.detection.detector import FEATURE_COLUMNS, AnomalyDetector
from sentrynet.detection.train import train


def _normal_flows(n=300, seed=0):
    rng = np.random.default_rng(seed)
    return pd.DataFrame(
        {
            "packet_count": rng.integers(5, 60, n),
            "avg_packet_size": rng.normal(600, 100, n),
            "byte_rate": rng.normal(4000, 800, n),
            "dst_port_entropy": rng.uniform(0.0, 1.0, n),
            "connection_rate": rng.uniform(0.0, 0.6, n),
            "syn_ack_ratio": rng.uniform(0.5, 1.5, n),
        }
    )


def _scan_flow():
    return pd.DataFrame(
        [
            {
                "packet_count": 400,
                "avg_packet_size": 60.0,
                "byte_rate": 4800.0,
                "dst_port_entropy": 8.5,
                "connection_rate": 80.0,
                "syn_ack_ratio": 400.0,
            }
        ]
    )


def test_score_adds_anomaly_columns():
    detector = AnomalyDetector().fit(_normal_flows())
    scored = detector.score(_normal_flows(n=10, seed=1))
    assert "anomaly_score" in scored.columns
    assert "is_anomaly" in scored.columns
    assert len(scored) == 10


def test_port_scan_flow_is_flagged():
    detector = AnomalyDetector().fit(_normal_flows())
    scan = detector.score(_scan_flow()).iloc[0]
    normal = detector.score(_normal_flows(n=100, seed=2))

    assert bool(scan["is_anomaly"]) is True
    assert scan["anomaly_score"] > normal["anomaly_score"].max()


def test_most_normal_flows_are_not_flagged():
    detector = AnomalyDetector().fit(_normal_flows())
    held_out = detector.score(_normal_flows(n=300, seed=3))
    assert held_out["is_anomaly"].mean() < 0.05


def test_score_before_fit_raises():
    with pytest.raises(RuntimeError):
        AnomalyDetector().score(_normal_flows(n=5))


def test_missing_feature_columns_raises():
    detector = AnomalyDetector().fit(_normal_flows())
    with pytest.raises(ValueError):
        detector.score(pd.DataFrame({"packet_count": [1]}))


def test_empty_baseline_raises():
    with pytest.raises(ValueError):
        AnomalyDetector().fit(pd.DataFrame(columns=FEATURE_COLUMNS))


def test_scoring_empty_flows_returns_empty_frame():
    detector = AnomalyDetector().fit(_normal_flows())
    scored = detector.score(pd.DataFrame(columns=FEATURE_COLUMNS))
    assert scored.empty
    assert "anomaly_score" in scored.columns


def test_save_and_load_roundtrip(tmp_path):
    detector = AnomalyDetector().fit(_normal_flows())
    model_path = tmp_path / "models" / "baseline.joblib"
    detector.save(model_path)

    loaded = AnomalyDetector.load(model_path)
    flows = _normal_flows(n=20, seed=4)
    pd.testing.assert_series_equal(
        detector.score(flows)["anomaly_score"],
        loaded.score(flows)["anomaly_score"],
    )


def test_train_from_csvs(tmp_path):
    csv_a = tmp_path / "baseline_a.csv"
    csv_b = tmp_path / "baseline_b.csv"
    _normal_flows(n=150, seed=5).to_csv(csv_a, index=False)
    _normal_flows(n=150, seed=6).to_csv(csv_b, index=False)
    model_path = tmp_path / "model.joblib"

    detector = train([str(csv_a), str(csv_b)], str(model_path))

    assert model_path.exists()
    assert detector.is_fitted

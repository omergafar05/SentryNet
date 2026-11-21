import json

import numpy as np
import pandas as pd

from sentrynet.detection.detect import detect, main
from sentrynet.detection.detector import FEATURE_COLUMNS, AnomalyDetector

SCAN_SRC = "10.0.0.66"


def _normal_flows(n, seed):
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


def _setup(tmp_path):
    """Train a model on normal flows, then write a CSV of normal flows plus one scan."""
    model_path = tmp_path / "model.joblib"
    AnomalyDetector().fit(_normal_flows(300, seed=0)).save(model_path)

    flows = _normal_flows(20, seed=1)
    flows["window"] = 1000
    flows["src_ip"] = "10.0.0.5"
    flows["dst_ip"] = "10.0.0.2"

    scan = {
        "packet_count": 400,
        "avg_packet_size": 60.0,
        "byte_rate": 4800.0,
        "dst_port_entropy": 8.5,
        "connection_rate": 80.0,
        "syn_ack_ratio": 400.0,
        "window": 1001,
        "src_ip": SCAN_SRC,
        "dst_ip": "10.0.0.2",
    }
    flows = pd.concat([flows, pd.DataFrame([scan])], ignore_index=True)

    csv_path = tmp_path / "flows.csv"
    flows.to_csv(csv_path, index=False)
    return model_path, csv_path


def test_detect_returns_only_anomalies_most_anomalous_first(tmp_path):
    model_path, csv_path = _setup(tmp_path)
    records = detect(str(model_path), str(csv_path))

    assert records, "expected the scan flow to be flagged"
    assert records[0]["src_ip"] == SCAN_SRC
    assert all(r["is_anomaly"] for r in records)
    scores = [r["anomaly_score"] for r in records]
    assert scores == sorted(scores, reverse=True)


def test_detect_all_returns_every_flow(tmp_path):
    model_path, csv_path = _setup(tmp_path)
    records = detect(str(model_path), str(csv_path), anomalies_only=False)
    assert len(records) == 21


def test_detect_records_are_json_ready_and_have_contract_fields(tmp_path):
    model_path, csv_path = _setup(tmp_path)
    records = detect(str(model_path), str(csv_path), anomalies_only=False)

    json.dumps(records)  # must not raise
    expected = {"window", "src_ip", "dst_ip", "anomaly_score", "is_anomaly", *FEATURE_COLUMNS}
    assert expected <= set(records[0])


def test_main_prints_json(tmp_path, capsys):
    model_path, csv_path = _setup(tmp_path)
    main([str(csv_path), "--model", str(model_path)])

    printed = json.loads(capsys.readouterr().out)
    assert isinstance(printed, list)
    assert any(r["src_ip"] == SCAN_SRC for r in printed)


def test_detect_on_header_only_csv_returns_empty_list(tmp_path):
    model_path, _ = _setup(tmp_path)
    empty_csv = tmp_path / "empty.csv"
    pd.DataFrame(columns=FEATURE_COLUMNS).to_csv(empty_csv, index=False)

    assert detect(str(model_path), str(empty_csv)) == []

"""Score a flow CSV with a trained model and return anomalies as JSON.

This is the handoff point for a backend: it reads the flow CSV that
sentrynet.pipeline writes and produces JSON records any service can consume.

Usage:
    python -m sentrynet.detection.detect data/flows.csv --model data/baseline_model.joblib
    python -m sentrynet.detection.detect data/flows.csv --model data/baseline_model.joblib --all
"""

from __future__ import annotations

import argparse
import json

import pandas as pd

from sentrynet.detection.detector import AnomalyDetector


def detect(model_path: str, flows_csv: str, anomalies_only: bool = True) -> list[dict]:
    """Score the flows in `flows_csv` and return JSON-ready records.

    Records are sorted most anomalous first. By default only flows the model
    flags as anomalous are returned; pass anomalies_only=False for every flow.
    """
    flows = pd.read_csv(flows_csv)
    scored = AnomalyDetector.load(model_path).score(flows)
    if anomalies_only:
        scored = scored[scored["is_anomaly"]]
    scored = scored.sort_values("anomaly_score", ascending=False)
    return json.loads(scored.to_json(orient="records"))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Score flows with a trained SentryNet model")
    parser.add_argument("flows_csv", help="flow CSV written by sentrynet.pipeline")
    parser.add_argument("--model", default="data/baseline_model.joblib")
    parser.add_argument("--all", action="store_true", help="return every flow, not just anomalies")
    args = parser.parse_args(argv)

    records = detect(args.model, args.flows_csv, anomalies_only=not args.all)
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()

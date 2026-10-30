"""Anomaly detection on flow features using an Isolation Forest.

Train on a baseline of normal traffic (flow rows from
features.flow_builder.build_flows), then score new flows. A higher
anomaly_score means the flow looks more unusual compared to the baseline.
"""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

FEATURE_COLUMNS = [
    "packet_count",
    "avg_packet_size",
    "byte_rate",
    "dst_port_entropy",
    "connection_rate",
    "syn_ack_ratio",
]


class AnomalyDetector:
    """Isolation Forest wrapper that scores flow rows against a baseline."""

    def __init__(self, contamination: float = 0.01, random_state: int = 42) -> None:
        self.model = IsolationForest(
            n_estimators=200,
            contamination=contamination,
            random_state=random_state,
        )
        self.is_fitted = False

    @staticmethod
    def _features(flows: pd.DataFrame) -> pd.DataFrame:
        missing = [c for c in FEATURE_COLUMNS if c not in flows.columns]
        if missing:
            raise ValueError(f"flows is missing feature columns: {missing}")
        return flows[FEATURE_COLUMNS].astype(float).fillna(0.0)

    def fit(self, flows: pd.DataFrame) -> "AnomalyDetector":
        """Learn what normal looks like from baseline flow rows."""
        if flows.empty:
            raise ValueError("cannot train on an empty baseline")
        self.model.fit(self._features(flows))
        self.is_fitted = True
        return self

    def score(self, flows: pd.DataFrame) -> pd.DataFrame:
        """Return a copy of `flows` with anomaly_score and is_anomaly columns."""
        if not self.is_fitted:
            raise RuntimeError("fit() or load() the detector before scoring")

        scored = flows.copy()
        if flows.empty:
            scored["anomaly_score"] = pd.Series(dtype=float)
            scored["is_anomaly"] = pd.Series(dtype=bool)
            return scored

        features = self._features(flows)
        scored["anomaly_score"] = -self.model.score_samples(features)
        scored["is_anomaly"] = self.model.predict(features) == -1
        return scored

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, path)

    @classmethod
    def load(cls, path: str | Path) -> "AnomalyDetector":
        detector = cls()
        detector.model = joblib.load(path)
        detector.is_fitted = True
        return detector

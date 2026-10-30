"""Train the baseline anomaly detector from captured flow CSVs.

Usage:
    python -m sentrynet.detection.train data/baseline_*.csv --out data/baseline_model.joblib
"""

from __future__ import annotations

import argparse
import glob
from typing import Iterable

import pandas as pd

from sentrynet.detection.detector import AnomalyDetector


def train(
    csv_paths: Iterable[str],
    out_path: str,
    contamination: float = 0.01,
) -> AnomalyDetector:
    """Fit a detector on one or more baseline flow CSVs and save it."""
    frames = [pd.read_csv(path) for path in csv_paths]
    if not frames:
        raise ValueError("no baseline CSVs given")

    baseline = pd.concat(frames, ignore_index=True)
    detector = AnomalyDetector(contamination=contamination).fit(baseline)
    detector.save(out_path)
    return detector


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the SentryNet baseline model")
    parser.add_argument("csvs", nargs="+", help="baseline flow CSVs (globs allowed)")
    parser.add_argument("--out", default="data/baseline_model.joblib")
    parser.add_argument("--contamination", type=float, default=0.01)
    args = parser.parse_args()

    # Expand globs ourselves so this also works on Windows shells.
    paths = sorted(p for pattern in args.csvs for p in (glob.glob(pattern) or [pattern]))
    train(paths, args.out, args.contamination)
    print(f"Trained on {len(paths)} file(s); model saved to {args.out}")


if __name__ == "__main__":
    main()

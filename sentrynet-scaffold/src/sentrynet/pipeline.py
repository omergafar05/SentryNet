"""Sprint 1 runner: capture live traffic -> flow features -> CSV.

Usage (needs admin/root for packet capture):
    sudo python -m sentrynet.pipeline --interface en0 --duration 300

On Windows, install Npcap first and run the terminal as Administrator.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Callable, Iterable

import pandas as pd

from sentrynet.capture.sniffer import PacketRecord, capture
from sentrynet.features.flow_builder import build_flows


def run(
    interface: str | None,
    duration: int,
    out_path: str | Path,
    capture_fn: Callable[[str | None, int], Iterable[PacketRecord]] = capture,
) -> pd.DataFrame:
    """Capture for `duration` seconds, build flow rows, and write them to CSV."""
    records = list(capture_fn(interface, duration))
    flows = build_flows(records)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    flows.to_csv(out_path, index=False)
    return flows


def main() -> None:
    parser = argparse.ArgumentParser(description="SentryNet capture + flow pipeline")
    parser.add_argument("--interface", default=None, help="network interface (e.g. en0, eth0)")
    parser.add_argument("--duration", type=int, default=300, help="capture length in seconds")
    parser.add_argument("--out", default="data/flows.csv", help="where to write the flow CSV")
    args = parser.parse_args()

    flows = run(args.interface, args.duration, args.out)
    print(flows.head(50).to_string(index=False))
    print(f"\n{len(flows)} flow rows written to {args.out}")


if __name__ == "__main__":
    main()

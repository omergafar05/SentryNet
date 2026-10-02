"""Time-windowed flow aggregation.

Sprint 1 scope: turn a stream of PacketRecords into flow-level
feature rows (one row per src/dst pair per time window).
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Iterable

import pandas as pd

from sentrynet.capture.sniffer import PacketRecord

WINDOW_SECONDS = 5


def _port_entropy(ports: list[int]) -> float:
    """Shannon entropy of the destination ports touched — high entropy
    can indicate scanning behavior."""
    if not ports:
        return 0.0
    counts = Counter(ports)
    total = len(ports)
    return -sum((c / total) * math.log2(c / total) for c in counts.values())


def build_flows(records: Iterable[PacketRecord]) -> pd.DataFrame:
    """Aggregate packet records into windowed flow feature rows.

    Returns a DataFrame with one row per (src_ip, dst_ip, window) with
    columns: packet_count, total_bytes, avg_packet_size,
    dst_port_entropy, syn_count, ack_count.
    """
    rows = []
    for rec in records:
        rows.append(
            {
                "window": int(rec.timestamp // WINDOW_SECONDS),
                "src_ip": rec.src_ip,
                "dst_ip": rec.dst_ip,
                "dst_port": rec.dst_port,
                "size": rec.size,
                "flags": rec.flags or "",
            }
        )

    if not rows:
        return pd.DataFrame(
            columns=[
                "window",
                "src_ip",
                "dst_ip",
                "packet_count",
                "total_bytes",
                "avg_packet_size",
                "dst_port_entropy",
                "syn_count",
                "ack_count",
            ]
        )

    df = pd.DataFrame(rows)

    flows = []
    for (window, src, dst), group in df.groupby(["window", "src_ip", "dst_ip"]):
        ports = [p for p in group["dst_port"].tolist() if p is not None]
        flows.append(
            {
                "window": window,
                "src_ip": src,
                "dst_ip": dst,
                "packet_count": len(group),
                "total_bytes": int(group["size"].sum()),
                "avg_packet_size": float(group["size"].mean()),
                "dst_port_entropy": _port_entropy(ports),
                "syn_count": int(group["flags"].str.contains("S").sum()),
                "ack_count": int(group["flags"].str.contains("A").sum()),
            }
        )

    return pd.DataFrame(flows)

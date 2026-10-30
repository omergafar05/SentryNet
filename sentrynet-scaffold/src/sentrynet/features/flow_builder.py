"""Time-windowed flow aggregation.

Turns a stream of PacketRecords into flow-level feature rows
(one row per src/dst pair per time window).
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Iterable

import pandas as pd

from sentrynet.capture.sniffer import PacketRecord

WINDOW_SECONDS = 5

FLOW_COLUMNS = [
    "window",
    "src_ip",
    "dst_ip",
    "packet_count",
    "total_bytes",
    "avg_packet_size",
    "byte_rate",
    "dst_port_entropy",
    "syn_count",
    "ack_count",
    "connection_rate",
    "syn_ack_ratio",
]


def _port_entropy(ports: list[int]) -> float:
    """Shannon entropy of the destination ports touched. High entropy
    can indicate scanning behavior."""
    if not ports:
        return 0.0
    counts = Counter(ports)
    total = len(ports)
    return -sum((c / total) * math.log2(c / total) for c in counts.values())


def build_flows(records: Iterable[PacketRecord]) -> pd.DataFrame:
    """Aggregate packet records into windowed flow feature rows.

    Returns a DataFrame with one row per (src_ip, dst_ip, window) and the
    columns in FLOW_COLUMNS:

    - byte_rate: total_bytes / WINDOW_SECONDS
    - connection_rate: SYN packets per second (new connection attempts)
    - syn_ack_ratio: syn_count / max(ack_count, 1). A SYN-ACK reply has both
      flags set, so it counts toward both. Many SYNs with few ACKs is the
      classic scan / SYN-flood shape.
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
        return pd.DataFrame(columns=FLOW_COLUMNS)

    df = pd.DataFrame(rows)

    flows = []
    for (window, src, dst), group in df.groupby(["window", "src_ip", "dst_ip"]):
        ports = [p for p in group["dst_port"].tolist() if pd.notna(p)]
        total_bytes = int(group["size"].sum())
        syn_count = int(group["flags"].str.contains("S").sum())
        ack_count = int(group["flags"].str.contains("A").sum())
        flows.append(
            {
                "window": window,
                "src_ip": src,
                "dst_ip": dst,
                "packet_count": len(group),
                "total_bytes": total_bytes,
                "avg_packet_size": float(group["size"].mean()),
                "byte_rate": total_bytes / WINDOW_SECONDS,
                "dst_port_entropy": _port_entropy(ports),
                "syn_count": syn_count,
                "ack_count": ack_count,
                "connection_rate": syn_count / WINDOW_SECONDS,
                "syn_ack_ratio": syn_count / max(ack_count, 1),
            }
        )

    return pd.DataFrame(flows, columns=FLOW_COLUMNS)

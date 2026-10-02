"""Live packet capture using Scapy.

Sprint 1 scope: capture raw packets on a given interface and yield
minimal per-packet records for the feature pipeline to aggregate.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

from scapy.all import sniff
from scapy.packet import Packet


@dataclass
class PacketRecord:
    """Minimal fields pulled off a captured packet."""

    timestamp: float
    src_ip: str
    dst_ip: str
    src_port: int | None
    dst_port: int | None
    protocol: str
    size: int
    flags: str | None  # TCP flags, if applicable


def _to_record(pkt: Packet) -> PacketRecord | None:
    """Convert a raw Scapy packet into a PacketRecord, or None if unsupported."""
    if not pkt.haslayer("IP"):
        return None

    ip_layer = pkt["IP"]
    src_port = dst_port = None
    protocol = "OTHER"
    flags = None

    if pkt.haslayer("TCP"):
        protocol = "TCP"
        src_port = pkt["TCP"].sport
        dst_port = pkt["TCP"].dport
        flags = str(pkt["TCP"].flags)
    elif pkt.haslayer("UDP"):
        protocol = "UDP"
        src_port = pkt["UDP"].sport
        dst_port = pkt["UDP"].dport

    return PacketRecord(
        timestamp=float(pkt.time),
        src_ip=ip_layer.src,
        dst_ip=ip_layer.dst,
        src_port=src_port,
        dst_port=dst_port,
        protocol=protocol,
        size=len(pkt),
        flags=flags,
    )


def capture(interface: str, duration: int = 30) -> Iterator[PacketRecord]:
    """Capture packets on `interface` for `duration` seconds.

    Yields PacketRecord instances. Requires elevated privileges
    (sudo / admin) on most systems.
    """
    packets = sniff(iface=interface, timeout=duration)
    for pkt in packets:
        record = _to_record(pkt)
        if record is not None:
            yield record


if __name__ == "__main__":
    # Quick manual smoke test: `python -m sentrynet.capture.sniffer`
    for rec in capture(interface="en0", duration=5):
        print(rec)

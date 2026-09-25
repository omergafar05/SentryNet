from sentrynet.capture.sniffer import PacketRecord
from sentrynet.features.flow_builder import build_flows


def _rec(t, src, dst, port, size, flags=""):
    return PacketRecord(
        timestamp=t,
        src_ip=src,
        dst_ip=dst,
        src_port=1234,
        dst_port=port,
        protocol="TCP",
        size=size,
        flags=flags,
    )


def test_build_flows_empty_input_returns_empty_dataframe():
    df = build_flows([])
    assert df.empty
    assert "packet_count" in df.columns


def test_build_flows_aggregates_same_window_and_pair():
    records = [
        _rec(t=0.0, src="10.0.0.1", dst="10.0.0.2", port=80, size=100, flags="S"),
        _rec(t=1.0, src="10.0.0.1", dst="10.0.0.2", port=80, size=200, flags="A"),
    ]
    df = build_flows(records)

    assert len(df) == 1
    row = df.iloc[0]
    assert row["packet_count"] == 2
    assert row["total_bytes"] == 300
    assert row["avg_packet_size"] == 150.0
    assert row["syn_count"] == 1
    assert row["ack_count"] == 1


def test_build_flows_separates_different_windows():
    records = [
        _rec(t=0.0, src="10.0.0.1", dst="10.0.0.2", port=80, size=100),
        _rec(t=10.0, src="10.0.0.1", dst="10.0.0.2", port=80, size=100),
    ]
    df = build_flows(records)
    assert len(df) == 2  # default WINDOW_SECONDS=5, so t=0 and t=10 differ


def test_build_flows_port_scan_has_high_entropy():
    records = [
        _rec(t=0.0, src="10.0.0.1", dst="10.0.0.2", port=p, size=60)
        for p in range(1, 21)
    ]
    df = build_flows(records)
    assert len(df) == 1
    assert df.iloc[0]["dst_port_entropy"] > 3.0  # spread across many ports

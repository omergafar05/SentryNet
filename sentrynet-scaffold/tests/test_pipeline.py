from sentrynet.capture.sniffer import PacketRecord
from sentrynet.pipeline import run


def _fake_capture(interface, duration):
    for t, port in [(0.0, 80), (1.0, 443)]:
        yield PacketRecord(
            timestamp=t,
            src_ip="10.0.0.1",
            dst_ip="10.0.0.2",
            src_port=1234,
            dst_port=port,
            protocol="TCP",
            size=100,
            flags="S",
        )


def test_run_writes_flow_csv(tmp_path):
    out = tmp_path / "out" / "flows.csv"
    flows = run("fake0", 1, out, capture_fn=_fake_capture)

    assert out.exists()
    assert len(flows) == 1
    assert flows.iloc[0]["packet_count"] == 2
    assert flows.iloc[0]["syn_count"] == 2

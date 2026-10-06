from sentrynet.capture.sniffer import PacketRecord
from sentrynet.features.flow_builder import build_flows


def test_missing_ports_do_not_inflate_entropy():
    records = [
        PacketRecord(
            timestamp=100.0 + i * 0.1,
            src_ip="192.0.2.1",
            dst_ip="192.0.2.2",
            src_port=None,
            dst_port=None,
            protocol="OTHER",
            size=98,
            flags=None,
        )
        for i in range(4)
    ]

    # A numeric port makes pandas convert missing ports to NaN.
    records.append(
        PacketRecord(
            timestamp=100.5,
            src_ip="192.0.2.3",
            dst_ip="192.0.2.4",
            src_port=50000,
            dst_port=443,
            protocol="TCP",
            size=60,
            flags="S",
        )
    )

    flows = build_flows(records)
    ping_flow = flows.loc[flows["src_ip"] == "192.0.2.1"].iloc[0]

    assert ping_flow["packet_count"] == 4
    assert ping_flow["total_bytes"] == 392
    assert ping_flow["dst_port_entropy"] == 0.0
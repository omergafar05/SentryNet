from sentrynet.capture.sniffer import PacketRecord, _to_record


class FakeLayer:
    def __init__(self, **fields):
        self.__dict__.update(fields)


class FakePacket(dict):
    """Minimal stand-in for a Scapy packet, keyed by layer name."""

    def haslayer(self, name):
        return name in self

    def __getitem__(self, name):
        return dict.__getitem__(self, name)

    @property
    def time(self):
        return 1234.5

    def __len__(self):
        return 60


def test_to_record_returns_none_without_ip_layer():
    pkt = FakePacket()
    assert _to_record(pkt) is None


def test_to_record_parses_tcp_packet():
    pkt = FakePacket()
    pkt["IP"] = FakeLayer(src="10.0.0.1", dst="10.0.0.2")
    pkt["TCP"] = FakeLayer(sport=1111, dport=80, flags="S")

    record = _to_record(pkt)

    assert isinstance(record, PacketRecord)
    assert record.src_ip == "10.0.0.1"
    assert record.dst_ip == "10.0.0.2"
    assert record.protocol == "TCP"
    assert record.dst_port == 80
    assert record.flags == "S"

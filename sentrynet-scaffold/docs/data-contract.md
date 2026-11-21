# SentryNet Data Contract

This document describes the two data formats other components (a backend, a
dashboard) rely on: the flow CSV that the capture pipeline writes, and the JSON
that the detector returns.

## 1. Flow CSV

Written by `python -m sentrynet.pipeline`. One row per source/destination pair
per 5-second window.

| Column | Type | Meaning |
|---|---|---|
| `window` | int | Window index. Window start in epoch seconds is `window * 5`. |
| `src_ip` | string | Source IP address |
| `dst_ip` | string | Destination IP address |
| `packet_count` | int | Packets in the window |
| `total_bytes` | int | Bytes in the window |
| `avg_packet_size` | float | Mean packet size in bytes |
| `byte_rate` | float | `total_bytes / 5`, bytes per second |
| `dst_port_entropy` | float | Shannon entropy of destination ports touched. High values suggest scanning. |
| `syn_count` | int | Packets with the SYN flag set |
| `ack_count` | int | Packets with the ACK flag set |
| `connection_rate` | float | `syn_count / 5`, SYN packets per second |
| `syn_ack_ratio` | float | `syn_count / max(ack_count, 1)`. SYN-ACK replies count toward both. |

## 2. Detector output (JSON)

Produced by `python -m sentrynet.detection.detect`, or by calling
`sentrynet.detection.detect.detect()` from Python. The output is a JSON array
of records, most anomalous first. Each record is a flow row (all columns above)
plus two fields:

| Field | Type | Meaning |
|---|---|---|
| `anomaly_score` | float | Roughly 0 to 1. Higher means the flow looks more unusual compared to the baseline. |
| `is_anomaly` | bool | `true` if the model flags the flow as anomalous |

By default only flows with `is_anomaly: true` are returned. Pass `--all` (or
`anomalies_only=False` in Python) to get every scored flow.

Illustrative record for a SYN scan:

```json
{
  "window": 354325000,
  "src_ip": "10.0.0.66",
  "dst_ip": "10.0.0.2",
  "packet_count": 400,
  "total_bytes": 24000,
  "avg_packet_size": 60.0,
  "byte_rate": 4800.0,
  "dst_port_entropy": 8.5,
  "syn_count": 400,
  "ack_count": 0,
  "connection_rate": 80.0,
  "syn_ack_ratio": 400.0,
  "anomaly_score": 0.658,
  "is_anomaly": true
}
```

Scores depend on the baseline the model was trained on, so the numbers above
will differ for your own traffic. Missing values are returned as `null`.

## 3. Commands

```bash
# Capture flows (needs admin/root)
sudo python -m sentrynet.pipeline --interface <iface> --duration 300 --out data/flows.csv

# Train on baseline captures
python -m sentrynet.detection.train data/baseline_*.csv --out data/baseline_model.joblib

# Score a capture and print anomalies as JSON
python -m sentrynet.detection.detect data/flows.csv --model data/baseline_model.joblib
```

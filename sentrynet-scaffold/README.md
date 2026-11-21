# SentryNet

**AI-augmented network traffic monitoring & SOC assistant**

SentryNet captures live network traffic, turns it into flow-level features, and uses unsupervised machine learning to flag anomalous behavior such as port scans and SYN floods. The long-term goal is to add LLM-generated incident summaries, mirroring at small scale the detection-and-response workflow of a Security Operations Center (SOC).

## Status

| Piece | State |
|---|---|
| Packet capture (Scapy) | Done |
| Flow feature extraction (pandas) | Done |
| Anomaly detection (Isolation Forest) | Done, tested on synthetic data |
| `detect` command (JSON output for a backend) | Done |
| Baseline capture of real traffic | In progress |
| Validation against `nmap` / `hping3` attacks | Planned |
| Severity / category classifier | Planned |
| LLM incident summaries (Claude API) | Planned |
| Backend and dashboard | In progress. The backend was built with a collaborator: [add their name here]. |

The detector has only been tested on synthetic flows so far. Detection rates and thresholds will be added after real baseline captures and attack validation.

## How it works

```
Live traffic (Scapy)
        |
        v
Time-windowed flow aggregation (pandas)
  -> byte rate, port entropy, connection rate, SYN/ACK ratio
        |
        v
Anomaly detection (Isolation Forest, scikit-learn)
  -> trained on a baseline of normal traffic
        |
        v
JSON anomalies (detect command)
        |
        v
Backend / dashboard
```

## Quickstart

```bash
pip install -e ".[dev]"
pytest tests/ -v

# 1. Capture flows (needs admin/root; on Windows install Npcap and use an Administrator terminal)
sudo python -m sentrynet.pipeline --interface <iface> --duration 300 --out data/baseline_browsing.csv

# 2. Train on one or more baseline captures
python -m sentrynet.detection.train data/baseline_*.csv --out data/baseline_model.joblib

# 3. Score a capture and print anomalies as JSON
sudo python -m sentrynet.pipeline --interface <iface> --duration 60 --out data/flows.csv
python -m sentrynet.detection.detect data/flows.csv --model data/baseline_model.joblib
```

Captured CSVs and trained models stay in `data/` and are not committed. See [docs/data-contract.md](docs/data-contract.md) for the exact CSV and JSON formats.

## Project layout

```
src/sentrynet/
  capture/sniffer.py         Scapy capture into PacketRecord objects
  features/flow_builder.py   windowed flow features
  detection/detector.py      Isolation Forest wrapper (fit, score, save, load)
  detection/train.py         train a model from baseline CSVs
  detection/detect.py        score a CSV, print anomalies as JSON
  pipeline.py                capture to flow CSV
tests/                       pytest suite
docs/                        project proposal, weekly updates, data contract
```

## Stack

Python, Scapy, pandas, scikit-learn. Planned: Claude API for incident summaries.

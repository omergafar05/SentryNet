# SentryNet

**AI-augmented network traffic monitoring & SOC assistant**

SentryNet is a lightweight pipeline that captures live network traffic, detects anomalous behavior using unsupervised machine learning, and uses an LLM to auto-generate analyst-style incident summaries — mirroring, at small scale, the detection-and-response workflow of a modern Security Operations Center (SOC).

## Why

Most SOC time goes into triage: staring at flagged events and writing up what happened. I built SentryNet to explore where AI genuinely helps in that workflow versus where it's just noise. The short answer: the AI layer is only as good as the feature engineering underneath it — good signal in, useful summaries out; bad signal in, confident nonsense out.

## How it works

```
Live traffic (Scapy)
        │
        ▼
Time-windowed flow aggregation (pandas)
  → packet size, inter-arrival time, port entropy, SYN/ACK ratio
        │
        ▼
Anomaly detection (Isolation Forest, scikit-learn)
  → trained on a self-collected baseline of "normal" traffic
        │
        ▼
Triage / classification
  → categorize flagged events by likely attack type
        │
        ▼
AI incident summaries (Claude API)
  → short, analyst-style write-up + severity rating
        │
        ▼
Live dashboard (Streamlit)
```

## Features

- Real-time packet capture and flow-level feature extraction
- Unsupervised anomaly detection — no labeled attack data required
- Validated against simulated attacks (`nmap` port scans, `hping3` SYN floods)
- LLM-generated incident summaries for faster triage
- Simple live dashboard for demoing detections end-to-end

## Stack

Python · Scapy · pandas · scikit-learn · Claude API · Streamlit

## Status

Actively in development. Current focus: capture and feature pipeline (see `Project Goals` in the [project proposal](./SentryNet_Project_Proposal.docx) for the full milestone breakdown).

## What I learned

Feature engineering matters more than model choice. An early version of the baseline wasn't normalized for time-of-day traffic patterns, which caused false positives during normal heavy-use windows — fixing that mattered more than any model tuning. The LLM summary layer is genuinely useful for triage speed, but it amplifies whatever signal quality it's given rather than correcting for it.

# 🚀 Automated CPU & Memory Metrics Collection from Prometheus

## 📌 Overview
Previously, to get CPU and Memory usage for Kubernetes nodes, we had to manually open Grafana and check metrics **pod by pod**:
- Max CPU Usage
- Max of Mean CPU Usage
- Max Memory Usage
- Max of Mean Memory Usage  

This was **time-consuming and tedious**.  

Now, this Python script **automates the process** by fetching all metrics **directly from Prometheus**:
- Collects metrics for **all pods at once**.
- Calculates **Max CPU, Max of Mean CPU, Max Memory, Max of Mean Memory** over the **last 7 days**.
- Achieves ~85% accuracy compared to manual checks.  

This reduces manual effort dramatically and ensures consistent results.

---

## ✅ Features
- Automatic retrieval of CPU & Memory metrics from Prometheus.
- Calculates for **all pods simultaneously**:
  - Max CPU Usage
  - Max of Mean CPU Usage
  - Max Memory Usage
  - Max of Mean Memory Usage
- Configurable time range and queries.
- Export results to **Excel** (or optionally Google Sheets).
- Reduces manual workload from “one-by-one pod checking” to a single script run.

---

## 🛠️ Tech Stack
- **Language:** Python 3.x
- **APIs:** Prometheus API
- **Libraries:**
  - `requests` (API calls)
  - `openpyxl` (Excel export)
  - `prometheus-api-client` (Prometheus data)
  - `gspread` & `oauth2client` (optional for Google Sheets integration)

---

## 🔑 Requirements
- Python 3.x
- Access to Prometheus instance
- Install dependencies:
```bash
pip install -r requirements.txt

import sys, os, requests
from datetime import datetime, timedelta
from openpyxl import Workbook, load_workbook
from prometheus_api_client import PrometheusConnect
from collections import defaultdict
import datetime as dt

NAMESPACE = "default"
STEP = "60s"

def get_label_values(PROMETHEUS_URL, metric, label, filters=None):
    filter_str = ""
    if filters:
        filter_parts = [f'{k}="{v}"' for k,v in filters.items()]
        filter_str = "{" + ",".join(filter_parts) + "}"
    query = f'series?match[]={metric}{filter_str}'
    
    try:
        resp = requests.get(f"{PROMETHEUS_URL}/api/v1/{query}", timeout=30)
        resp.raise_for_status()
        data = resp.json().get("data", [])
        values = set()
        for item in data:
            if label in item:
                values.add(item[label])
        return list(values)
    except Exception as e:
        print("Error fetching label values:", e)
        return []



def run_prometheus_query(prometheus_url, query):
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)
    step = 60
    try:
        response = requests.get(
            f"{prometheus_url}/api/v1/query_range",
            params={
                "query": query,
                "start": start_time.timestamp(),
                "end": end_time.timestamp(),
                "step": step,
            },
            timeout=60,
        )
        if not response.ok:
            print("QUERY:\n", query)
            print("STATUS:", response.status_code)
            print("BODY:", response.text)
            response.raise_for_status()
        result = response.json().get("data", {}).get("result", [])
        values_all = []
        for item in result:
            values_all.extend(float(v[1]) for v in item.get("values", []))
        if not values_all:
            return 0, 0
        return max(values_all), (sum(values_all) / len(values_all))
    except Exception as e:
        print("Error running query:", e)
        return 0, 0

def get_cpu_stats_for_pod(prometheus_url, pod_name: str):
    query = f"""
sum(rate(container_cpu_usage_seconds_total{{namespace="{NAMESPACE}", pod="{pod_name}"}}[5m])) by (pod,instance) * 1000 * 100 * 100
/ sum(container_spec_cpu_quota{{namespace="{NAMESPACE}", pod="{pod_name}"}}) by (pod,instance)
"""
    return run_prometheus_query(prometheus_url, query)

def get_memory_stats_for_deployment(prometheus_url, deployment_name):
    try:
        prom = PrometheusConnect(url=prometheus_url, disable_ssl=True)
        end_time = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
        start_time = end_time - dt.timedelta(days=7)
        query = f"""
            (sum(container_memory_working_set_bytes{{pod=~"{deployment_name}-.*", namespace="{NAMESPACE}", container!="POD"}}) by (pod)
            /
            sum(container_spec_memory_limit_bytes{{pod=~"{deployment_name}-.*", namespace="{NAMESPACE}", container!="POD"}}) by (pod)) * 100
        """
        memory_data = prom.custom_query_range(
            query=query, start_time=start_time, end_time=end_time, step=STEP
        )
        if not memory_data:
            return 0, 0
        all_values = [float(v[1]) for item in memory_data for v in item['values']]
        max_usage = max(all_values) if all_values else 0
        daily_values = defaultdict(list)
        for item in memory_data:
            for ts_str, val_str in item['values']:
                dt_obj = dt.datetime.fromtimestamp(float(ts_str), dt.timezone.utc)
                daily_values[dt_obj.date()].append(float(val_str))
        daily_means = [sum(v)/len(v) for v in daily_values.values() if v]
        max_of_mean_daily_usage = max(daily_means) if daily_means else 0
        return round(max_usage, 2), round(max_of_mean_daily_usage, 2)
    except Exception as e:
        print(f"Memory query error for {deployment_name}: {e}")
        return 0, 0

if __name__ == "__main__":
    # Ask user for Prometheus URL
    # PROMETHEUS_URL = input("👉 Enter Prometheus URL (e.g. http://localhost:9090): ").strip()
    PROMETHEUS_URL = os.environ.get("PROMETHEUS_URL")
    if not PROMETHEUS_URL:
      print("PROMETHEUS_URL env variable not set. Please pass from Jenkins.")
    sys.exit(1)
    if not PROMETHEUS_URL:
        print("❌ Prometheus URL is required. Exiting...")
        sys.exit(1)

    deployments_file = "data.xlsx"
    containers = get_label_values(PROMETHEUS_URL, "kube_pod_container_info", "container", {"namespace":NAMESPACE})
    containers.sort()
    DEPLOYMENTS = containers
    if not DEPLOYMENTS:
        print("❌ No deployments found in Excel. Exiting...")
        sys.exit(1)

    wb = Workbook()
    ws = wb.active
    ws.title = "Pod Stats"
    ws.append(["Deployment", "Max_CPU (%)", "Mean_CPU (%)", "Max_Memory (%)", "Max_of_Daily_Mean_Memory (%)"])

    for DEPLOYMENT_NAME in DEPLOYMENTS:
        print(PROMETHEUS_URL,DEPLOYMENT_NAME)
        pods = get_label_values(PROMETHEUS_URL, "kube_pod_container_info", "pod", {"namespace": "default", "container": DEPLOYMENT_NAME})
        if not pods:
            print(f"⚠️ No pods found for {DEPLOYMENT_NAME}")
            continue

        max_cpu_overall, max_mean_cpu_overall = 0, 0
        for pod in pods:
            pod_max_cpu, pod_mean_cpu = get_cpu_stats_for_pod(PROMETHEUS_URL, pod)
            if pod_max_cpu > max_cpu_overall:
                max_cpu_overall = pod_max_cpu
            if pod_mean_cpu > max_mean_cpu_overall:
                max_mean_cpu_overall = pod_mean_cpu

        max_mem, max_mean_mem = get_memory_stats_for_deployment(PROMETHEUS_URL, DEPLOYMENT_NAME)

        print(f"\n⚡ {DEPLOYMENT_NAME}:")
        print(f"CPU → Max: {max_cpu_overall:.2f}% | Mean: {max_mean_cpu_overall:.2f}%")
        print(f"Memory → Max: {max_mem:.2f}% | Max of Daily Mean: {max_mean_mem:.2f}%")

        ws.append([
            DEPLOYMENT_NAME,
            round(max_cpu_overall, 2),
            round(max_mean_cpu_overall, 2),
            max_mem,
            max_mean_mem
        ])

    filename = "pod_summary_with_memory.xlsx"
    wb.save(filename)
    print(f"\n📊 Summary saved to {filename}")


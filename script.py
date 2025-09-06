import requests
from datetime import datetime, timedelta
from openpyxl import Workbook
from prometheus_api_client import PrometheusConnect
from collections import defaultdict
import datetime as dt

PROMETHEUS_URL = "http://172.80.16.10:30090"
NAMESPACE = "default"
STEP = "60s"

# List of deployments you want to check
DEPLOYMENTS = [
    "aerospike-qa1",
    "altair-ft-edge-qa",
    "auto-apply-jobposting-cron-qa",
    "blackbox-exporter",
    "cassowary-qa",
    "chat-module-service-qa",
    "chat-module-service-ui-qa",
    "common-cms-banner-mgt-api-qa",
    "contact-info-management-api-calls-qa",
    "core-altair-solr-bulk-actions-qa",
    "core-altair-solr-profile-movement-qa",
    "core-altair-solr-qa",
    "dashboard-apis-qa",
    "dashboard-metrics-scraper",
    "edge-contact-blacklist-qa",
    "edge-contact-engine-direct-requests-qa",
    "fm-search-edge-rt-qa",
    "job-dedupe-service-qa",
    "job-ingestion-service-qa",
    "koyo-campaign-app-qa",
    "koyo-edge-contact-engine-qa",
    "koyo-engine-contact-svc-qa",
    "koyo-engine-monstercore-svc-qa",
    "koyo-engine-search-svc-qa",
    "koyo-qa",
    "named-entity-recognition-cron-qa",
    "named-entity-recognition-qa",
    "parrot-rec4-foundit-qa",
    "parrot-rec4-qa",
    "parrot-rec4-sms-qa",
    "parrot-send-rabbitmq-mail-qa",
    "pigeon-rec4-foundit-qa",
    "pigeon-rec4-qa",
    "pigeon-send-rabbitmq-mail-qa",
    "polaris-edge-qa",
    "polaris-qa",
    "pollux-qa",
    "python3scraperequest-qa",
    "rec-edge-cron-qa",
    "recruiter-actions-rabbitmq-qa",
    "recruiter-admin-platform-qa",
    "recruiter-ats-edge-gateway-qa",
    "recruiter-cdp-edge-ui-qa",
    "recruiter-common-cron-service-all-active-corp",
    "recruiter-common-cron-service-corp-archival-details",
    "recruiter-common-cron-service-corp-communication",
    "recruiter-common-cron-service-corp-services-archival",
    "recruiter-common-cron-service-ip-location",
    "recruiter-common-cron-service-login-logs-archive",
    "recruiter-company-logo-service-qa",
    "recruiter-edge-actions-consumer-qa",
    "recruiter-edge-actions-qa",
    "recruiter-edge-assessments-integrator-qa",
    "recruiter-edge-dashboard-canary-qa",
    "recruiter-edge-dashboard-qa",
    "recruiter-edge-dashboard-ui-canary-qa",
    "recruiter-edge-dashboard-ui-qa",
    "recruiter-edge-ecom-services-qa",
    "recruiter-edge-event-tracking-qa",
    "recruiter-edge-excel-qa",
    "recruiter-edge-folder-management-ui-qa",
    "recruiter-edge-foldermanagement-cron-qa",
    "recruiter-edge-foldermanagement-qa",
    "recruiter-edge-header-qa",
    "recruiter-edge-hoatzin-qa",
    "recruiter-edge-job-posting-qa",
    "recruiter-edge-jobposting-ui-qa",
    "recruiter-edge-jobs-masterdata-qa",
    "recruiter-edge-manage-jobposting-ui-qa",
    "recruiter-edge-manage-save-search-qa",
    "recruiter-edge-managejobposting-qa",
    "recruiter-edge-opt-out-qa",
    "recruiter-edge-opt-out-ui-qa",
    "recruiter-edge-platform-reports-ui-qa",
    "recruiter-edge-platform-user-management-ui-qa",
    "recruiter-edge-questionnaires-qa",
    "recruiter-edge-resume-conversion-qa",
    "recruiter-image-migration-qa",
    "recruiter-outreach-scheduling-consumer-qa",
    "recruiter-session-apis-qa",
    "recruiter-srp-edge-qa",
    "recruiter-srp-edge-ui-qa",
    "recruiter-whatsapp-edge-api-qa",
    "recruiter-whatsapp-event-consumer-qa",
    "recruiter-whatsapp-scheduling-consumer-qa",
    "recruiter4-actions-qa",
    "recruiter4-cdp-api-edge-qa",
    "recruiter4-cdp-api-edge-ui-qa",
    "recruiter4-cdp-api-qa",
    "recruiter4-chat-module-service-qa",
    "recruiter4-common-utils-ui-qa1",
    "recruiter4-config-qa",
    "recruiter4-dashboard-qa",
    "recruiter4-dedupe-service-qa",
    "recruiter4-discovery-qa",
    "recruiter4-django-cms-canary-qa",
    "recruiter4-django-cms-qa",
    "recruiter4-folder-management-qa",
    "recruiter4-folder-management-ui-qa",
    "recruiter4-gateway-qa",
    "recruiter4-general-scripts-qa",
    "recruiter4-hoatzin-qa",
    "recruiter4-jobposting-cron-jobs-qa",
    "recruiter4-jobposting-service-qa",
    "recruiter4-jobs-feed-qa",
    "recruiter4-login-qa",
    "recruiter4-manage-save-search-cron-qa",
    "recruiter4-manage-save-search-qa",
    "recruiter4-manage-save-search-ui-qa",
    "recruiter4-managejobposting-qa",
    "recruiter4-managejobposting-ui-qa",
    "recruiter4-masterdata-service-qa",
    "recruiter4-newjobposting-ui-qa",
    "recruiter4-outreach-edge-api-qa",
    "recruiter4-outreach-edge-send-mail-consumer-qa",
    "recruiter4-outreach-edge-send-mail-producer-qa",
    "recruiter4-outreach-edge-send-sms-consumer-qa",
    "recruiter4-outreach-email-campaign-listing-edge-ui-qa",
    "recruiter4-outreach-email-edge-ui-qa",
    "recruiter4-peacock-qa",
    "recruiter4-personal-folder-ui-qa",
    "recruiter4-recruitersrp-v4-qa",
    "recruiter4-search-metric-qa",
    "recruiter4-search-service-qa",
    "recruiter4ats-pull-jobs-service-qa",
    "recruiter4ats-qa",
    "redis-qa1",
    "refgen-qa",
    "resume-enrichment-qa",
    "resume-parser-core-integration-qa",
    "search-synonyms-qa",
    "similar-companies-recruiter-qa",
    "socialjobsads-qa",
    "unified-altair-qa",
    "unified-koyo-altair-qa"
]

# ----------------- PROMQL CPU FUNCTIONS ----------------- #
def get_pods_of_deployment(deployment_name):
    query = f'series?match[]=container_cpu_usage_seconds_total{{namespace="{NAMESPACE}",pod=~"{deployment_name}-.*"}}'
    try:
        response = requests.get(f"{PROMETHEUS_URL}/api/v1/{query}")
        response.raise_for_status()
        data = response.json()
        pods = set()
        for item in data.get("data", []):
            pod_name = item.get("pod")
            if pod_name:
                pods.add(pod_name)
        return list(pods)
    except Exception as e:
        print("Error fetching pod list:", e)
        return []

def get_cpu_stats_for_pod(pod_name: str):
    query = f"""
sum(rate(container_cpu_usage_seconds_total{{namespace="{NAMESPACE}", pod="{pod_name}"}}[5m])) by (pod,instance) * 1000 * 100 * 100
/ sum(container_spec_cpu_quota{{namespace="{NAMESPACE}", pod="{pod_name}"}}) by (pod,instance)
"""
    return run_prometheus_query(query)

def run_prometheus_query(query):
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)
    step = 60
    try:
        response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query_range",
            params={
                "query": query,
                "start": start_time.timestamp(),
                "end": end_time.timestamp(),
                "step": step,
            },
            timeout=30,
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

# ----------------- PROMQL MEMORY FUNCTIONS ----------------- #
def get_memory_stats_for_deployment(deployment_name):
    """
    For given deployment, fetch overall max memory and max of daily mean memory for last 7 days.
    """
    try:
        prom = PrometheusConnect(url=PROMETHEUS_URL, disable_ssl=True)
        end_time = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
        start_time = end_time - dt.timedelta(days=7)

        query = f"""
            (sum(container_memory_working_set_bytes{{pod=~"{deployment_name}-.*", namespace="{NAMESPACE}", container!="POD"}}) by (pod)
            /
            sum(container_spec_memory_limit_bytes{{pod=~"{deployment_name}-.*", namespace="{NAMESPACE}", container!="POD"}}) by (pod)) * 100
        """

        memory_data = prom.custom_query_range(
            query=query,
            start_time=start_time,
            end_time=end_time,
            step=STEP
        )

        if not memory_data:
            return 0, 0

        all_values = [float(v[1]) for item in memory_data for v in item['values']]
        max_usage = max(all_values) if all_values else 0

        daily_values = defaultdict(list)
        for item in memory_data:
            for timestamp_str, value_str in item['values']:
                dt_object = dt.datetime.fromtimestamp(float(timestamp_str), dt.timezone.utc)
                day_key = dt_object.date()
                daily_values[day_key].append(float(value_str))

        daily_means = []
        for day in daily_values:
            if daily_values[day]:
                daily_means.append(sum(daily_values[day]) / len(daily_values[day]))

        max_of_mean_daily_usage = max(daily_means) if daily_means else 0

        return round(max_usage, 2), round(max_of_mean_daily_usage, 2)
    except Exception as e:
        print(f"Memory query error for {deployment_name}: {e}")
        return 0, 0

# ----------------- MAIN EXECUTION ----------------- #
if __name__ == "__main__":
    wb = Workbook()
    ws = wb.active
    ws.title = "Pod Stats"
    ws.append(["Deployment", "Max_CPU (%)", "Mean_CPU (%)", "Max_Memory (%)", "Max_of_Daily_Mean_Memory (%)"])

    for DEPLOYMENT_NAME in DEPLOYMENTS:
        pods = get_pods_of_deployment(DEPLOYMENT_NAME)
        if not pods:
            print(f"⚠️ No pods found for {DEPLOYMENT_NAME}")
            continue

        max_cpu_overall, max_cpu_pod = 0, ""
        max_mean_cpu_overall, max_mean_cpu_pod = 0, ""

        for pod in pods:
            pod_max_cpu, pod_mean_cpu = get_cpu_stats_for_pod(pod)
            if pod_max_cpu > max_cpu_overall:
                max_cpu_overall, max_cpu_pod = pod_max_cpu, pod
            if pod_mean_cpu > max_mean_cpu_overall:
                max_mean_cpu_overall, max_mean_cpu_pod = pod_mean_cpu, pod

        max_mem, max_mean_mem = get_memory_stats_for_deployment(DEPLOYMENT_NAME)

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

# import requests

# def get_label_values(prom_url, metric, label, filters=None):
#     filter_str = ""
#     if filters:
#         filter_parts = [f'{k}="{v}"' for k,v in filters.items()]
#         filter_str = "{" + ",".join(filter_parts) + "}"
#     query = f'series?match[]={metric}{filter_str}'
    
#     try:
#         resp = requests.get(f"{prom_url}/api/v1/{query}", timeout=30)
#         resp.raise_for_status()
#         data = resp.json().get("data", [])
#         values = set()
#         for item in data:
#             if label in item:
#                 values.add(item[label])
#         return list(values)
#     except Exception as e:
#         print("Error fetching label values:", e)
#         return []

# PROM_URL =  "http://172.80.16.10:30090"



# # Example: fetch containers in namespace "default"
# containers = get_label_values(PROM_URL, "kube_pod_container_info", "container", {"namespace": "default"})
# # print("Containers:", containers)

# containers.sort()
# data = containers
# # for item in containers:
# #     print(item)


# # print(data)
# print(len(data))

# for item in data:
#     pods = get_label_values(PROM_URL, "kube_pod_container_info", "pod", {"namespace": "default", "container": item})
#     print("*************************",item,"**************************************")
#     print(len(pods))
#     print(pods)



# # Example: fetch pods for a container





import requests

def get_label_values(prom_url, metric, label, filters=None):
    filter_str = ""
    if filters:
        filter_parts = [f'{k}="{v}"' for k,v in filters.items()]
        filter_str = "{" + ",".join(filter_parts) + "}"
    # ❌ pehle aap series use kar rahe the
    # query = f'series?match[]={metric}{filter_str}'
    
    # ✅ ab hum query endpoint use karenge jo sirf current values laata hai
    query = f'query?query={metric}{filter_str}'
    
    try:
        resp = requests.get(f"{prom_url}/api/v1/{query}", timeout=30)
        resp.raise_for_status()
        data = resp.json().get("data", {}).get("result", [])
        values = set()
        for item in data:
            metric_labels = item.get("metric", {})
            if label in metric_labels:
                values.add(metric_labels[label])
        return list(values)
    except Exception as e:
        print("Error fetching label values:", e)
        return []

PROM_URL = "http://172.80.16.10:30090"

# Example: fetch containers in namespace "default"
containers = get_label_values(
    PROM_URL,
    "kube_pod_container_info",
    "container",
    {"namespace": "default"}
)

containers.sort()
print("Total containers:", len(containers))

for item in containers:
    pods = get_label_values(
        PROM_URL,
        "kube_pod_status_phase",
        "pod",
        {"namespace": "default", "phase": "Running"}
    )
    print("*************************", item, "**************************************")
    print("Running pods count:", len(pods))
    print(pods)

from prometheus_client import start_http_server, Gauge
import requests
import time

NIFI_URL_CLUSTER = "http://192.168.144.135:8999/nifi-api/controller/cluster"

# Create gauge metrics to measure NiFi metrics
nifi_address_gauge = Gauge('nifi_address', 'NiFi Address', ['address'])
nifi_status_gauge = Gauge('nifi_status', 'NiFi Status', ['address', 'status'])
nifi_active_thread_count_gauge = Gauge('nifi_active_thread_count', 'NiFi Active Thread Count', ['address'])
nifi_queued_gauge = Gauge('nifi_queued', 'NiFi Queued', ['address'])

# Start the HTTP server to expose the metrics
start_http_server(addr='192.168.144.2', port=8000)

def get_nifi_metrics():
    response = requests.get(NIFI_URL_CLUSTER)
    if (response.status_code != 200):
        raise ConnectionError("Cannot get info from cluster")
        return

    data = response.json()
    nodes = data['cluster']['nodes']

    for node in nodes:
        address = node['address']
        status = node['status']
        active_thread_count = node['activeThreadCount']
        queued = node['queued']

        queued_value = queued.split(' / ')[0]
        queued_unit = queued.split(' / ')[1]

        # Update the gauge metrics
        nifi_address_gauge.labels(address).set(1)
        nifi_status_gauge.labels(address, status).set(1)
        nifi_active_thread_count_gauge.labels(address).set(active_thread_count)
        nifi_queued_gauge.labels(address).set(int(queued_value))

while True:
    get_nifi_metrics()
    time.sleep(10)

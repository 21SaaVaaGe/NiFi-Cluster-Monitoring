from prometheus_client import start_http_server, Gauge
import requests
import time

nifi_cluster_urls = [
    "http://192.168.144.135:8999/nifi-api/controller/cluster",
    "http://192.168.144.136:8999/nifi-api/controller/cluster"
]

nifi_address_metric = Gauge('nifi_address', 'NiFi Address', ['address'])
nifi_status_metric = Gauge('nifi_status', 'NiFi Status', ['address', 'status'])
nifi_active_thread_count_metric = Gauge('nifi_active_thread_count', 'NiFi Active Thread Count', ['address'])
nifi_queued_metric = Gauge('nifi_queued', 'NiFi Queued', ['address'])

start_http_server(addr='192.168.144.2', port=8000)


def get_nifi_metrics():
    for url in nifi_cluster_urls:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            nodes = data['cluster']['nodes']
            nifi_status_metric.clear()
            for node in nodes:
                address = node.get('address')
                status = node.get('status')
                active_thread_count = node.get('activeThreadCount', 0)
                queued = node.get('queued')
                if queued:
                    queued_value = queued.split(' / ')[0]
                    queued_unit = queued.split(' / ')[1]
                else:
                    queued_value = 0
                    queued_unit = ''
                nifi_address_metric.labels(address).set(1)
                if status == "DISCONNECTED":
                    nifi_status_metric.labels(address, status).set(0)
                else:
                    nifi_status_metric.labels(address, status).set(1)
                nifi_active_thread_count_metric.labels(address).set(active_thread_count)
                nifi_queued_metric.labels(address).set(int(queued_value))
            break
    else:
        nifi_address_metric.labels('').set(0)
        nifi_status_metric.labels('', '').set(0)
        nifi_active_thread_count_metric.labels('').set(0)
        nifi_queued_metric.labels('').set(0)

while True:
    get_nifi_metrics()
    time.sleep(10)

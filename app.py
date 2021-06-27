import json
import socket
import subprocess
from typing import Any, Dict
from flask import Flask, jsonify
from prometheus_client import Counter, Gauge, generate_latest

app = Flask(__name__)

last_time = ""

# temp_counter = Counter('temp', 'Temperature endpoint queries', ['temp'])

# CPU Metrics
temp_gauge = Gauge('temp_in_celcius', 'The temp of the CPU in celcius')
# Memory Metrics
used_mem_mb_gauge = Gauge('used_mem_mb',
                          'The used memory of the node in MB',
                          ['memory_data'])

# Data Model Keys
node_name_key = "node_name"
timestamp_key = "timestamp"
# Memory Model Keys
total_mem_key = "total_memory_mb"
used_mem_key = "used_memory_mb"


@app.route("/metrics")
def metrics():
    get_metrics()
    get_mem_metrics()
    return generate_latest()


def remove_metric_fields(json_data: Dict[str, Any]) -> Dict[str, Any]:
    if json_data.get(node_name_key) is not None:
        del json_data[node_name_key]
    if json_data.get(timestamp_key) is not None:
        del json_data[timestamp_key]
    return json_data


def get_mem_metrics():
    json_data_str = "{}"
    with open('/app/mon/mem_info.json', 'r') as json_file:
        json_data_str = json_file.read()
    json_data = json.loads(json_data_str)
    json_data = remove_metric_fields(json_data)
    used_mem = json_data.get(used_mem_key)
    if used_mem is not None:
        total_mem = json_data.get(total_mem_key)
        md = {'total_memory': total_mem}
        used_mem_mb_gauge.labels(memory_data=md).set(used_mem)


def get_metrics() -> Dict[str, Any]:
    global last_time
    json_data_str = "{}"
    with open('/app/mon/cpu_info.json', 'r') as json_file:
        json_data_str = json_file.read()
    json_data = json.loads(json_data_str)
    # Remove duplicate keys
    if json_data.get(timestamp_key) is not None:
        last_time = json_data[timestamp_key]
    json_data = remove_metric_fields(json_data)
    # Remove values that dont have temps
    json_data['items'] = [x for x in json_data['items']
                          if "temp1" in x.keys()]
    # FIXME
    # Add data
    json_data['_ipAddress'] = socket.gethostbyname(socket.gethostname())
    json_data['_name'] = socket.gethostname()
    app.logger.info(json_data)
    app.logger.info(last_time)
    # Increment prom counter
    # temp_counter.labels(temp=json_data).inc()
    if len(json_data['items']) == 1:
        # Check if first char is numeric, if not strip it off
        temp_str = json_data['items'][0]['temp1']
        start_idx = 0
        if not str(temp_str[0]).isnumeric():
            start_idx = 1
        temp_num = temp_str[start_idx:-2]
        app.logger.info(temp_num)
        temp_gauge.set(temp_num)
    return json_data


@app.route("/")
def index():
    return "Hello friend"


@app.route("/local")
def local_cmd():
    # Piping commands example
    f = open('/tmp/test', 'w+')
    cmd = "echo hello there dude"
    cmd2 = "grep the /tmp/test"
    subprocess.run(cmd.split(' '), stdout=f, text=True)
    output2 = subprocess.run(cmd2.split(' '), text=True)
    if output2.returncode != 0:
        app.logger.info("ouches")
    else:
        app.logger.info(output2.stdout)
    return "done"


@app.route("/temp")
def temp_cmd():
    json_data = get_metrics()
    return jsonify(json_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

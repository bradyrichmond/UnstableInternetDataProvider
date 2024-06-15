import subprocess
from time import sleep, time
import requests
from uuid import uuid4
import sys
import json

google_dns = "8.8.8.8"

def main():
    print("Starting application")
    global endpoint
    endpoint = sys.argv[1]
    global gateway
    gateway = sys.argv[2]
    start_pinging()

def ping(ip):
    ping_success = subprocess.run(["ping", "-c", "1", ip], capture_output=True)
        
    if (ping_success.returncode == 0):
        ping_success_string = str(ping_success.stdout)
        time_value_index = ping_success_string.index('time') + 5
        latency = ping_success_string[time_value_index:].split(' ')[0]
        return latency
    else:
        print('failure')
        return float('inf')

def start_pinging():
    gateway = ping_gateway()
    google = ping_google_dns()
    send_values([gateway, google])
    sleep(10)
    start_pinging()

def ping_google_dns():
    return ping(google_dns)

def ping_gateway():
    return ping(gateway)

def send_values(values):
    id = uuid4()
    ping_time = round(time() * 1000)

    data = json.dumps({
        "id": str(id),
        "ping_time": str(ping_time),
        "gateway": {
            "latency": values[0],
            "ip": "Gateway"
        },
        "google": {
            "latency": values[1],
            "ip": google_dns
        }
    })

    # print(data)

    try:
        print('sending db update')
        response = requests.post(url = endpoint, data = data)
        response.raise_for_status()
    except:
        print('failed request')

if __name__ == "__main__":
    main()
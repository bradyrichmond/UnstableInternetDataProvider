import subprocess
from time import sleep, time
import requests
from uuid import uuid4
import sys
import json


def main():
    print("Starting application")
    global endpoint
    endpoint = sys.argv[1]
    ping_google_dns()

def ping_google_dns():
    ping_success = subprocess.run(["ping", "-c", "1", "8.8.8.8"], capture_output=True)
        
    if (ping_success.returncode == 0):
        ping_success_string = str(ping_success.stdout)
        time_value_index = ping_success_string.index('time') + 5
        latency = ping_success_string[time_value_index:].split(' ')[0]
        send_success(latency)
    else:
        print('failure')

    sleep(10)
    ping_google_dns()

def send_success(latency):
    id = uuid4()
    ping_time = round(time() * 1000)
    data = json.dumps({
        "id": str(id),
        "ping_time": str(ping_time),
        "latency": str(latency)
    })

    try:
        print('sending db update')
        response = requests.post(url = endpoint, data = data)
        response.raise_for_status()
    except:
        print('failed request')

if __name__ == "__main__":
    main()
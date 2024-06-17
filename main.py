import subprocess
from time import sleep, time
import requests
from uuid import uuid4
import sys
import json
from platform import node

google_dns = "8.8.8.8"
failed_pings = []
ping_count = 0

def main():
    print("Starting application")
    global endpoint
    endpoint = sys.argv[1]
    global gateway
    gateway = sys.argv[2]
    send_script_break_to_db()
    while True:
        global ping_count
        ping_action()
        ping_count += 1
        sleep(10)

def print_test():
    print('test')

def send_script_break_to_db():
    send_values(["0", "0"])

def ping(ip):
    ping_success = subprocess.run(["ping", "-c", "1", ip], capture_output=True)
        
    if (ping_success.returncode == 0):
        ping_success_string = str(ping_success.stdout)
        time_value_index = ping_success_string.index('time') + 5
        latency = ping_success_string[time_value_index:].split(' ')[0]

        return latency
    else:
        print('failure')
        return "0"

def ping_action():
    gateway = ping_gateway()
    google = ping_google_dns()
    send_values([gateway, google])

def ping_google_dns():
    return ping(google_dns)

def ping_gateway():
    return ping(gateway)

def send_values(values):
    id = uuid4()
    ping_time = round(time() * 1000)

    raw = {
        "pk": node(),
        "sk":f'{str(ping_time)}',
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
    }

    data = json.dumps(raw)

    if (values[1] == "-1"):
        print('google ping failed, adding to failed ping')
        failed_pings.append(raw)
    else:
        if (len(failed_pings) > 0):
            print(f'Catching up after down time. {len(failed_pings)} failed pings, approximating {len(failed_pings) * 10 / 60} minutes of downtime')
            catch_up()

        try:
            print('sending db update')
            response = requests.post(url = endpoint, data = data)
            response.raise_for_status()
        except:
            print('failed request')

def catch_up():
    global failed_pings
    if (len(failed_pings) <= 25):
        response = requests.post(url = f'{endpoint}/catchUp', data = json.dumps(failed_pings))
        response.raise_for_status()
        failed_pings = []
    else:
        group = failed_pings[:25]
        remaining = failed_pings[25:]
        response = requests.post(url = f'{endpoint}/catchUp', data = json.dumps(group))
        response.raise_for_status()
        failed_pings = remaining
        catch_up()

if __name__ == "__main__":
    main()
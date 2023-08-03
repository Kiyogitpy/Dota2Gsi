import requests
import time

def send_request(minutes, seconds):
    clock_time = minutes * 60 + seconds
    data = {
        "map": {
            "clock_time": clock_time
        }
    }
    
    requests.post("http://127.0.0.1:3000/", json=data)

for minutes in range(60): # 0 to 59 minutes
    for seconds in range(60): # 0 to 59 seconds
        send_request(minutes, seconds)
        time.sleep(1) # Wait for 1 second between requests

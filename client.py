import requests
import time



def send_request(minutes, seconds):
    clock_time = minutes * 60 + seconds
    data = {
        "map": {
            "clock_time": clock_time
        }
    }
    try:
        requests.post("http://127.0.0.1:3000/", json=data)
    except requests.exceptions.RequestException as e:
        print("An error occurred while sending the request:",e)
    

for minutes in range(60): # 0 to 59 minutes
    for seconds in range(60): # 0 to 59 seconds
        send_request(minutes, seconds)
        time.sleep(1) # Wait for 1 second between requests

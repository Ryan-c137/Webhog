import threading
import time
import requests
import json
from grabber import sys_info_grabber, network_info_grabber, ports_processes_info_grabber

# Get information that can get from grabber, raw but rich
def collecting_oneshot():

    sys_info = sys_info_grabber()
    network_info = network_info_grabber()
    (listening_ports_tuples, established_ports_tuples) = ports_processes_info_grabber()

    listening_ports_number = len(listening_ports_tuples)
    established_connections_number = len(established_ports_tuples)

    sent = network_info['sent']
    recv = network_info['recv']
    cpu_usage = sys_info['cpu_percent']

    info = {
        'listening_ports_number': listening_ports_number,
        'established_connections_number': established_connections_number,
        'sent': sent,
        'recv': recv,
        'cpu_usage': cpu_usage
    }

    return info;

# Sending snapshots to AI API, and return the processed answer
def sender_receiver():
    API_key = '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'
    prompt = 'tell me the answer of 1+1, no more words'

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_key}",
        },
        data=json.dumps({
            "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
            "messages": [{
                "role": "user",
                "content": f"{prompt}"
            }]
        })
    )

    if response.status_code == 200:
        print(response.json()['choices'][0]['message']['content'])
    else:
        print(f"Error {response.status_code}: {response.text}")



class DataCollector:

    def __init__(self):
        self.thread = None
        self.stop_event = threading.Event()
        self.cache = []
        self.window = 20

    def start(self):
        if self.thread and self.thread.is_alive(): return
        
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        if self.thread: self.thread.join(timeout=5)
    
    def _cache_cleaner(self):
        while(len(self.cache) > self.window):
            self.cache.pop(0)

    def _collecting(self):
        self.lastshot = collecting_oneshot()
        self.correntshot = collecting_oneshot()
        snapshot = {
            'timestamp': time.time(),
            'listening_ports_number': self.correntshot['listening_ports_number'],
            'established_connections_number': self.correntshot['established_connections_number'],
            'sent_MBps': self.correntshot['sent'],
            'recv_MBps': self.correntshot['recv'],
            'connections_number_changed': self.correntshot['established_connections_number'] - self.lastshot['established_connections_number'],
            'cpu_usage': self.correntshot['cpu_usage']
        }
        self.cache.append(snapshot)
        self.lastshot = self.correntshot
        self._cache_cleaner()
        print(self.cache)

    def _run(self):
        while not self.stop_event.is_set():
            print("is running...")
            while(1):
                self._collecting()
            self.stop_event.wait(2)

collector = DataCollector()
collector.start()
time.sleep(10)
collector.stop()

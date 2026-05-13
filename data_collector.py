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
def sender_receiver(cache):
    API_key = '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'
    prompt = 'I am goint to feed you 20 snapshots of a server(' \
             'Each entry containsconnection counts, bytes transferred, and CPU usage) ' \
             'of networking information of a machine, and please give me' \
             ' the score of network security roisk from 0 to 100. Be careful with analysing. ' \
             'But for result, I want a number between 0 to 100 as score of risk, pure and simple. ' 
    
    json_cache = json.dumps(cache)

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_key}",
        },
        data=json.dumps({
            "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
            "messages": [{
                "role": "user",
                "content": f"{prompt} \n {json_cache}"
            }]
        })
    )

    if response.status_code == 200:
        # print(response.json()['choices'][0]['message']['content'])
        return response.json()['choices'][0]['message']['content']
    else:
        # print(f"Error {response.status_code}: {response.text}")
        return None



class DataCollector:

    def __init__(self):
        self.thread = None
        self.stop_event = threading.Event()
        self.cache = []
        self.window = 20
        self.risk_score = -1

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
        if(len(self.cache) >= 20): self.risk_score = sender_receiver(self.cache)
        # else: print('Collecting enough data for analysing.\n', len(self.cache))
        # print(self.cache)
        # print(len(self.cache))

    def _run(self):
        while not self.stop_event.is_set():
            print("is running...")
            while(1):
                self._collecting()
            self.stop_event.wait(2)

collector = DataCollector()
collector.start()
time.sleep(300)
collector.stop()

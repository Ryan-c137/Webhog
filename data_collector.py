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
    API_key = '[YOUR API KEY]'
    prompt = 'I am goint to feed you 20 snapshots of a server(' \
             'Each entry containsconnection counts, bytes transferred, and CPU usage) ' \
             'of networking information of a machine, and please give me' \
             ' the score of network security risk from 0 to 100. Do not give false alarm!' \
             ' If the score is higher than 60, you need to provide a short but clear reason why you think' \
             'it has a potential risk of network security. ' \
             'But for result, I want a number between 0 to 100 as score of risk. ' \
             'If the score is between 0 to 60, the reply should just be plain score.' \
             'And if score is higher than 60, the reason can be attached after score.' \
             'I need the reply follow this format restrictively:' \
             'For score under 60, just score as the only outcome;' \
             'For score more than 60, the reply should be pure score, with reason right after it. '

    
    json_cache = json.dumps(cache)

    response = requests.post(
        # TODO: adjust this part to match your service provider
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_key}",
        },
        data=json.dumps({
            # deepseek/deepseek-v4-flash:free
            "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
            # "model": "deepseek/deepseek-v4-flash:free",
            "messages": [{
                "role": "user",
                "content": f"{prompt} \n {json_cache}"
            }]
        })
    )

    if response.status_code == 200:
        # print(response.json()['choices'][0]['message']['content'])
        return response.json()['choices'][0]['message']['content']
    # else:
    #     # print(f"Error {response.status_code}: {response.text}")
    #     return None



class DataCollector:

    def __init__(self):
        self.thread = None
        self.stop_event = threading.Event()
        self.cache = []
        self.window = 20
        self.risk_score = -1
        self.cache_size = 0
        self.reason = ''

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
        self.currentshot = collecting_oneshot()
        snapshot = {
            'timestamp': time.time(),
            'listening_ports_number': self.currentshot['listening_ports_number'],
            'established_connections_number': self.currentshot['established_connections_number'],
            'sent_MBps': self.currentshot['sent'],
            'recv_MBps': self.currentshot['recv'],
            'connections_number_changed': self.currentshot['established_connections_number'] - self.lastshot['established_connections_number'],
            'cpu_usage': self.currentshot['cpu_usage']
        }
        self.cache.append(snapshot)
        self.lastshot = self.currentshot
        self._cache_cleaner()
        self.cache_size = len(self.cache)
        print(self.cache_size)
        # DEBUGING
        if(self.cache_size >= 20): 
            reply = sender_receiver(self.cache)

            # print(reply)

            risk_score_current = str(reply).split()[0] 
            if(risk_score_current is not None and int(risk_score_current) >= 0): 
                # time.sleep(5)
                self.risk_score = int(risk_score_current)
                if(self.risk_score >= 60):
                    self.reason = str(reply).split(maxsplit=1)[1] if str(reply).split(maxsplit=1)[1] is not None else 'No clear reason.'

    def _run(self):
        while not self.stop_event.is_set():
            print("is running...")
            while(1):
                self._collecting()
            self.stop_event.wait(2)

collector = DataCollector()

if __name__ == '__main__':
    collector.start()
    time.sleep(10000)

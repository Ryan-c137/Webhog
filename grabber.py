import psutil
import time
import yaml
import subprocess

def sys_info_grabber():

    # Calculate the real memory usage
    memory = psutil.virtual_memory()
    total = memory.total / (1024**3)
    free = memory.available / (1024**3)
    used = total - free
    percentage = used / total * 100

    info = {
        'cpu_percent': psutil.cpu_percent(interval=1, percpu=True),
        'cpu_core_numbers': psutil.cpu_count(),
        'cpu_frequency': psutil.cpu_freq()._asdict(),
        'memory_percentage': percentage,
        'memory_total': total,
        'memory_used': used,
        'memory_free': free,
        'disk_usage_percentage': psutil.disk_usage('/').percent,
        }
    print(yaml.dump(info))
    return info

def network_info_grabber():
    net_io = psutil.net_io_counters()
    sent_1 = net_io.bytes_sent
    recv_1 = net_io.bytes_recv
    time.sleep(1)
    net_io = psutil.net_io_counters()
    sent_2 = net_io.bytes_sent
    recv_2 = net_io.bytes_recv

    # Data snet and received speed
    sent = (sent_2 - sent_1) / 125000;
    recv = (recv_2 - recv_1) / 125000; #Mbps

    # Get active network interface information
    internet_interface_active = []
    for interface, addrs in psutil.net_if_addrs().items():
        interface_info = {'name': interface}

        for addr in addrs:
            if addr.family.name == 'AF_INET':
                interface_info['ipv4'] = addr.address
            elif addr.family.name == 'AF_INET6':
                interface_info['ipv6'] = addr.address
            elif addr.family.name == 'AF_LINK':
                interface_info['mac'] = addr.address
        
        if 'ipv4' in interface_info and 'ipv6' in interface_info and 'mac' in interface_info:
            internet_interface_active.append(interface_info)

    info = {
        'sent': sent,
        'recv': recv,
        'active': internet_interface_active
    } 

    print(yaml.dump(info))
    print(info['active'][0]['name'])

    return info

def main():
    sys_info_grabber()
    network_info_grabber()

if __name__ == '__main__':
    main()

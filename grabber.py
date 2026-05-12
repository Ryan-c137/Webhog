import psutil
import time
import yaml

def sys_info_grabber():

    # Calculate the real memory usage
    memory = psutil.virtual_memory()
    total = memory.total / (1024**3)
    free = memory.available / (1024**3)
    used = total - free
    percentage = used / total * 100

    info = {
        'cpu_percent': psutil.cpu_percent(interval=1, percpu=False),
        'cpu_core_numbers': psutil.cpu_count(),
        'cpu_frequency': psutil.cpu_freq()._asdict(),
        'memory_percentage': percentage,
        'memory_total': total,
        'memory_used': used,
        'memory_free': free,
        'disk_usage_percentage': psutil.disk_usage('/').percent,
        }
    # print(yaml.dump(info))
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

    # print(yaml.dump(info))
    # print(info['active'][0]['name'])

    return info

def ports_processes_info_grabber():
    listening_ports = []
    established_ports = []

    connections = psutil.net_connections()

    for con in connections:
        if con.status == 'NONE' or not con.laddr:
            continue

        if con.status not in ['LISTEN', 'ESTABLISHED']:
            continue
        
        port_info = {
            'port': con.laddr.port,
            'local_address': con.laddr.ip,
            'remote_address_ip': con.raddr.ip if con.raddr else 'N/A',
            'remote_address_port': con.raddr.port if con.raddr else 'N/A',
            'pid': con.pid,
        }

        try:
            process = psutil.Process(con.pid)
            port_info['process'] = process.name()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            port_info['process'] = 'Unknown'

        if con.status == 'LISTEN':
            listening_ports.append(port_info)
        else:
            established_ports.append(port_info)

    # print(yaml.dump(listening_ports))
    # print(yaml.dump(established_ports))

    # Have to turn them into tuples in an array, so can be fed into tables
    listening_ports_tuples = []
    for l in listening_ports:
        listening_ports_tuples.append((l['port'], l['local_address'], l['process'], l['pid']))
    
    established_ports_tuples = []
    for e in established_ports:
        established_ports_tuples.append((e['port'], e['local_address'], e['remote_address_ip'], e['remote_address_port'], e['process'], e['pid']))

    # Sort by port number so the table doesn't jump around on refresh
    listening_ports_tuples.sort(key=lambda r: int(r[0]))
    established_ports_tuples.sort(key=lambda r: int(r[0]))

    return listening_ports_tuples, established_ports_tuples

def main():
    sys_info_grabber()
    network_info_grabber()
    ports_processes_info_grabber()

if __name__ == '__main__':
    main()

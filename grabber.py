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

    # network io infomation




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

def main():
    sys_info_grabber()

if __name__ == '__main__':
    main()

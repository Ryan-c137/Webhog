from textual.app import App, ComposeResult
from textual.widgets import ProgressBar, Static
from textual.containers import Horizontal, Vertical
from grabber import sys_info_grabber, network_info_grabber
import asyncio


# The display of all the system information
class SystemInfoDisplay(Horizontal):

    CSS_PATH = 'gui.tcss'

    def compose(self) -> ComposeResult:

        # Get information
        info = sys_info_grabber()

        # This is the block for CPU information
        with Vertical(classes='block') as v1:
            v1.border_title = 'CPU Information'
            with Vertical(classes='cpu') as v2:
                v2.border_title = 'CPU Cores Usage Percentage'
                with Horizontal(classes='bar'):
                    yield ProgressBar(total=100, id='core_1_2', show_eta=False)
                    yield Static('  1&2')

                with Horizontal(classes='bar'):
                    yield ProgressBar(total=100, id='core_3_4', show_eta=False)
                    yield Static('  3&4')

                with Horizontal(classes='bar'):
                    yield ProgressBar(total=100, id='core_5_6', show_eta=False)
                    yield Static('  5&6')

                with Horizontal(classes='bar'):
                    yield ProgressBar(total=100, id='core_7_8', show_eta=False)
                    yield Static('  7&8')
            yield Static('Current CPU Frequency: ' + str(info['cpu_frequency']['current']), id='cpu_frequency', classes='status')
            yield Static('Maximum CPU Frequency: ' + str(info['cpu_frequency']['max']), classes='status')
            yield Static('Minimum CPU Frequency: ' + str(info['cpu_frequency']['min']), classes='status')

        # Disk and Memory infomation part
        with Vertical(classes='block disk_memory') as v3:
            v3.border_title = 'Disk and Memory'
            yield Static('Memory Usage: ')
            yield ProgressBar(total=100, id='memory_percentage', show_eta=False)
            yield Static('Total Memory Space: ' + str(info['memory_total']) + '  GB', classes='status')
            yield Static('Used Memory Space: ' + str(info['memory_used']) + '  GB', id='memory_used', classes='status')
            yield Static('Free Memory Space: ' + str(info['memory_free']) + '  GB', id='memory_free', classes='status')
            yield Static('Disk Usage Percentage:')
            yield ProgressBar(total=100, id='disk', show_eta=False)

        # Get network information here
        info = network_info_grabber()
        # network hardware information
        with Vertical(classes='block network') as v4:
            v4.border_title = 'Network IO'
            yield Static('Activated Network Interface: ' + info['active'][0]['name'], id='name', classes='status')
            yield Static('IPv4 address: ' + info['active'][0]['ipv4'], id='ipv4', classes='status')
            yield Static('IPv6 address: ' + info['active'][0]['ipv6'], id='ipv6', classes='status')
            yield Static('MAC address: ' + info['active'][0]['name'], id='mac', classes='status')
            yield Static('Data Sending Speed: ' + str(info['sent']) + ' Mbps', id='sent', classes='status')
            yield Static('Data Receiving Speed: ' + str(info['recv']) + ' Mbps', id='recv', classes='status')



    async def on_mount(self):
        self.set_interval(0.3, self.update_info)
        await self.update_info()

    async def update_info(self):
        # Update system informtaion
        info = sys_info_grabber()
        bar1 = self.query_one('#core_1_2')
        bar1.progress = info['cpu_percent'][0] + info['cpu_percent'][1]
        bar2 = self.query_one('#core_3_4')
        bar2.progress = info['cpu_percent'][2] + info['cpu_percent'][3]
        bar3 = self.query_one('#core_5_6')
        bar3.progress = info['cpu_percent'][4] + info['cpu_percent'][5]
        bar4 = self.query_one('#core_7_8')
        bar4.progress = info['cpu_percent'][6] + info['cpu_percent'][7]
        cpu_frequency = self.query_one('#cpu_frequency')
        cpu_frequency.update('Current CPU Frequency: ' + str(info['cpu_frequency']['current']))
        memory_percentage = self.query_one('#memory_percentage')
        memory_percentage.progress = info['memory_percentage']
        memory_used = self.query_one('#memory_used')
        memory_used.update('Used Memory Space: ' + str(info['memory_used']) + '  GB')
        memory_free = self.query_one('#memory_free')
        memory_free.update('Free Memory Space: ' + str(info['memory_free']) + '  GB')
        disk = self.query_one('#disk')
        disk.progress = info['disk_usage_percentage']

        # Update network information
        info = network_info_grabber()
        name = self.query_one('#name')
        name.update('Activated Network Interface: ' + info['active'][0]['name'])
        ipv4 = self.query_one('#ipv4')
        ipv4.update('IPv4 address: ' + info['active'][0]['ipv4'])
        ipv6 = self.query_one('#ipv6')
        ipv6.update('IPv6 address: ' + info['active'][0]['ipv6'])
        mac = self.query_one('#mac')
        mac.update('MAC address: ' + info['active'][0]['mac'])
        sent = self.query_one('#sent')
        sent.update('Data Sending Speed: ' + str(info['sent']) + ' Mbps')
        recv = self.query_one('#recv')
        recv.update('Data Receiving Speed: ' + str(info['recv']) + ' Mbps')


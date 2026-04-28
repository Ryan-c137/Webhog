from textual.app import App, ComposeResult
from textual.widgets import ProgressBar, Static, DataTable
from textual.containers import Horizontal, Vertical
from grabber import ports_processes_info_grabber
import psutil


class PortsSockets(Vertical):
    CSS_PATH = 'gui.tcss'
    
    def compose(self) -> ComposeResult:
        
        with Vertical(classes='panel ports') as ports:
            ports.border_title = 'Ports & Processes'
            # Table for Listening ports
            yield Static('Listening Ports', classes='status')
            yield DataTable(id='listening', cursor_type='row')
            # Table for connection established ports
            yield Static('Connection Established Ports', classes='status')
            yield DataTable(id='established', cursor_type='row')

    async def on_mount(self):

        # inistialising 
        listening = self.query_one('#listening', DataTable)
        listening.add_columns('Port', 'Address', 'Process', 'PID')

        established = self.query_one('#established', DataTable)
        established.add_columns('Port', 'Local Address', 'Connected Address IP', 'Connected Address Port', 'Process', 'PID')

        self.set_interval(1, self.update_info)
        await self.update_info()

    async def update_info(self):
        listening_ports_tuples, established_ports_tuples = ports_processes_info_grabber()    

        listening = self.query_one('#listening', DataTable)
        listening.clear()
        for l in listening_ports_tuples:
            listening.add_row(*l) # Feed tutples into rows
        
        established = self.query_one('#established', DataTable)
        established.clear()
        for e in established_ports_tuples:
            established.add_row(*e)

